import csv
import chardet
import unicodedata

def detect_encoding(file_path):
    with open(file_path, 'rb') as file:
        raw_data = file.read()
        result = chardet.detect(raw_data)
    return result['encoding']

def escape_quotes(text):
    return text.replace("'", "\\'")

def normalize_text(text):
    text = unicodedata.normalize('NFKD', text)
    text = text.replace('‚Äô', "'").replace('‚Äî', '--').replace('‚Ä¶', '...')
    text = text.replace('‚Äî', '-').replace('‚Äô', "'")
    return text

def generate_cypher_queries(csv_file_path):
    encoding = detect_encoding(csv_file_path)
    print(f"Detected encoding: {encoding}")

    node_queries = []
    relationship_queries = []

    with open(csv_file_path, mode='r', newline='', encoding=encoding) as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            title = escape_quotes(normalize_text(row['title']))

            node_query = (
                f'CREATE (s:Show {{id: "{row["show_id"]}", type: "{row["type"]}", title: "{title}", '
                f'release_year: {row["release_year"]}, rating: "{row["rating"]}", '
                f'duration: "{row["duration"]}"}})'
            )
            node_queries.append(node_query)

            if row['director']:
                directors = row['director'].split(', ')
                for director in directors:
                    director_query = (
                        f'MERGE (d:Director {{name: "{escape_quotes(director)}"}})\n'
                        f'MERGE (d)-[:DIRECTS]->(s)'
                    )
                    relationship_queries.append(director_query)

            if row['cast']:
                cast_members = row['cast'].split(', ')
                for cast_member in cast_members:
                    cast_query = (
                        f'MERGE (a:Actor {{name: "{escape_quotes(cast_member)}"}})\n'
                        f'MERGE (a)-[:ACTS_IN]->(s)'
                    )
                    relationship_queries.append(cast_query)

            if row['country']:
                countries = row['country'].split(', ')
                for country in countries:
                    country_query = (
                        f'MERGE (c:Country {{name: "{escape_quotes(country)}"}})\n'
                        f'MERGE (s)-[:PRODUCED_IN]->(c)'
                    )
                    relationship_queries.append(country_query)

            if row['listed_in']:
                genres = row['listed_in'].split(', ')
                for genre in genres:
                    genre_query = (
                        f'MERGE (g:Genre {{name: "{escape_quotes(genre)}"}})\n'
                        f'MERGE (s)-[:LISTED_IN]->(g)'
                    )
                    relationship_queries.append(genre_query)

    return node_queries, relationship_queries

csv_file_path = './netflix_titles.csv'
nodes, relationships = generate_cypher_queries(csv_file_path)

with open('node_queries.cypher', 'w', encoding='utf-8') as node_file:
    node_file.write("\n".join(nodes))

with open('relationship_queries.cypher', 'w', encoding='utf-8') as rel_file:
    rel_file.write("\n".join(relationships))

print("Cypher queries have been written to 'node_queries.cypher' and 'relationship_queries.cypher'")
