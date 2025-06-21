import spacy
import networkx as nx
import pandas as pd
import json

# Load the spaCy model
nlp = spacy.load('en_core_web_lg')

def extract_entities(text):
    doc = nlp(text)
    entities = [(ent.text, ent.label_) for ent in doc.ents]
    return entities

def extract_relationships(doc):
    relations = []
    for token in doc:
        if token.dep_ in ('attr', 'dobj'):
            subject = [w for w in token.head.lefts if w.dep_ == 'nsubj']
            if subject:
                relations.append((subject[0], token, token.head))
        elif token.dep_ == 'pobj' and token.head.dep_ == 'prep':
            relations.append((token.head.head, token.head, token))
    return relations

def build_knowledge_graph(data):
    G = nx.Graph()
    
    for paragraph in data:
        doc = nlp(paragraph)
        entities = extract_entities(paragraph)
        relations = extract_relationships(doc)
        
        for entity, label in entities:
            G.add_node(entity, label=label)
        
        for subj, verb, obj in relations:
            G.add_edge(subj.text, obj.text, relation=verb.lemma_)
    
    return G

def read_data_from_csv(file_path):
    df = pd.read_csv(file_path)
    paragraphs = df['paragraphs'].dropna().tolist()
    return paragraphs

def save_graph_to_json(graph, filename='graph.json'):
    data = {
        'nodes': [{'id': node, 'label': data.get('label', 'No label')} for node, data in graph.nodes(data=True)],
        'edges': [{'source': u, 'target': v, 'relation': data.get('relation', 'No relation')} for u, v, data in graph.edges(data=True)]
    }
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)

if __name__ == "__main__":
    csv_file = input("Enter the CSV file path: ")
    paragraphs = read_data_from_csv(csv_file)
    G = build_knowledge_graph(paragraphs)
    
    print("Nodes:", G.nodes(data=True))
    print("Edges:", G.edges(data=True))

    # Save the graph to a JSON file
    save_graph_to_json(G, filename='knowledge_graph.json')
    print("Knowledge Graph saved to 'knowledge_graph.json'.")
