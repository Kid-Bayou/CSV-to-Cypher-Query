import csv
import chardet
import unicodedata

def detect_encoding(file_path):
    # Detect file encoding
    with open(file_path, 'rb') as file:
        raw_data = file.read()
        result = chardet.detect(raw_data)
    return result['encoding']

def escape_quotes(text):
    # Function to escape single quotes in Cypher using Unicode
    return text.replace("'", "\\u0027")

def normalize_text(text):
    # Normalize and replace problematic characters
    text = unicodedata.normalize('NFKD', text)
    text = text.replace('‚Äô', "'").replace('‚Äî', '--').replace('‚Ä¶', '...')
    text = text.replace('‚Äî', '-').replace('‚Äô', "'")
    text = text.replace('—', '--')  # Replace em dash with two hyphens
    return text

def generate_cypher_queries(csv_file_path):
    # Detect the encoding of the file
    encoding = detect_encoding(csv_file_path)
    print(f"Detected encoding: {encoding}")

    # Lists to hold Cypher queries
    node_queries = []
    relationship_queries = []

    # Open the CSV file with the detected encoding
    with open(csv_file_path, mode='r', newline='', encoding=encoding) as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            # Escape and normalize strings
            title = escape_quotes(normalize_text(row['title']))
            description = escape_quotes(normalize_text(row['description']))

            # Create a Show node with attributes
            node_query = (
                f"CREATE (s:Show {{id: '{row['show_id']}', type: '{row['type']}', title: '{title}', "
                f"release_year: {row['release_year']}, rating: '{row['rating']}', "
                f"duration: '{row['duration']}', description: '{description}'}})"
            )
            node_queries.append(node_query)

            # Create Director nodes and relationships
            if row['director']:
                directors = row['director'].split(', ')
                for director in directors:
                    director_query = (
                        f"MERGE (d:Director {{name: '{escape_quotes(director)}'}})\n"
                        f"MERGE (d)-[:DIRECTS]->(s)"
                    )
                    relationship_queries.append(director_query)

            # Create Actor nodes and relationships
            if row['cast']:
                cast_members = row['cast'].split(', ')
                for cast_member in cast_members:
                    cast_query = (
                        f"MERGE (a:Actor {{name: '{escape_quotes(cast_member)}'}})\n"
                        f"MERGE (a)-[:ACTS_IN]->(s)"
                    )
                    relationship_queries.append(cast_query)

            # Create Country nodes and relationships
            if row['country']:
                countries = row['country'].split(', ')
                for country in countries:
                    country_query = (
                        f"MERGE (c:Country {{name: '{escape_quotes(country)}'}})\n"
                        f"MERGE (s)-[:PRODUCED_IN]->(c)"
                    )
                    relationship_queries.append(country_query)

            # Create Genre nodes and relationships
            if row['listed_in']:
                genres = row['listed_in'].split(', ')
                for genre in genres:
                    genre_query = (
                        f"MERGE (g:Genre {{name: '{escape_quotes(genre)}'}})\n"
                        f"MERGE (s)-[:LISTED_IN]->(g)"
                    )
                    relationship_queries.append(genre_query)

    return node_queries, relationship_queries

# Example usage
csv_file_path = './netflix_titles.csv'  # Replace with your CSV file path
nodes, relationships = generate_cypher_queries(csv_file_path)

# Write node queries to a file
with open('node_queries.cypher', 'w', encoding='utf-8') as node_file:
    node_file.write("\n".join(nodes))

# Write relationship queries to a file
with open('relationship_queries.cypher', 'w', encoding='utf-8') as rel_file:
    rel_file.write("\n".join(relationships))

print("Cypher queries have been written to 'node_queries.cypher' and 'relationship_queries.cypher'")
