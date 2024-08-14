import csv
import chardet
import unicodedata

def detect_encoding(file_path):
    with open(file_path, 'rb') as file:
        raw_data = file.read()
        result = chardet.detect(raw_data)
    return result['encoding']

def escape_quotes(text):
    text = text.replace('"', '\\"')
    text = text.replace("'", "\\'")
    return text

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
    node_counter = 0

    with open(csv_file_path, mode='r', newline='', encoding=encoding) as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            node_counter += 1
            var_s = f's{node_counter}'

            title = escape_quotes(normalize_text(row['title']))

            node_query = (
                f'CREATE ({var_s}:Show {{id: "{row["show_id"]}", type: "{row["type"]}", title: "{title}", '
                f'release_year: {row["release_year"]}, rating: "{row["rating"]}", '
                f'duration: "{row["duration"]}"}})'
            )
            node_queries.append(node_query)

            if row['director']:
                directors = row['director'].split(', ')
                for i, director in enumerate(directors):
                    var_d = f'd{node_counter}_{i}'
                    director_query = (
                        f'MERGE ({var_d}:Director {{name: "{escape_quotes(director)}"}})\n'
                        f'MERGE ({var_d})-[:DIRECTS]->({var_s})'
                    )
                    relationship_queries.append(director_query)

            if row['cast']:
                cast_members = row['cast'].split(', ')
                for i, cast_member in enumerate(cast_members):
                    var_a = f'a{node_counter}_{i}'
                    cast_query = (
                        f'MERGE ({var_a}:Actor {{name: "{escape_quotes(cast_member)}"}})\n'
                        f'MERGE ({var_a})-[:ACTS_IN]->({var_s})'
                    )
                    relationship_queries.append(cast_query)

            if row['country']:
                countries = row['country'].split(', ')
                for i, country in enumerate(countries):
                    var_c = f'c{node_counter}_{i}'
                    country_query = (
                        f'MERGE ({var_c}:Country {{name: "{escape_quotes(country)}"}})\n'
                        f'MERGE ({var_s})-[:PRODUCED_IN]->({var_c})'
                    )
                    relationship_queries.append(country_query)

            if row['listed_in']:
                genres = row['listed_in'].split(', ')
                for i, genre in enumerate(genres):
                    var_g = f'g{node_counter}_{i}'
                    genre_query = (
                        f'MERGE ({var_g}:Genre {{name: "{escape_quotes(genre)}"}})\n'
                        f'MERGE ({var_s})-[:LISTED_IN]->({var_g})'
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
