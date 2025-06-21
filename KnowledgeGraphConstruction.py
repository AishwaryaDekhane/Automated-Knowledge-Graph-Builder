import spacy    # Importing spaCy, a library for NLP
import networkx as nx       # Importing NetworkX, a library for graph manipulation
import pandas as pd     # Importing pandas, a library for data manipulation
import json     # Importing json, a library for JSON manipulation

# Load the spaCy model
nlp = spacy.load('en_core_web_lg')      # Loading the large English NLP model from spaCy

# Function to extract named entities from text
def extract_entities(text):
    doc = nlp(text)     # Process the text using the spaCy model
    # Extracting entities and their labels from the processed text
    entities = [(ent.text, ent.label_) for ent in doc.ents] #sentense splitting tokanization- named entities in the document 
    return entities #list of entities and labels

# Function to extract relationships between entities from the processed document# Function to extract relationships between entities from the processed document
def extract_relationships(doc):
    relations = []
    for token in doc:       # Iterate through each token in the document
        if token.dep_ in ('attr', 'dobj'):      # Check if the token is an attribute or direct object
            subject = [w for w in token.head.lefts if w.dep_ == 'nsubj']        
            if subject:
                relations.append((subject[0], token, token.head))       # Append the relationship (subject, token, head) to the list
        elif token.dep_ == 'pobj' and token.head.dep_ == 'prep':        # Check if the token is an object of a preposition
            # Append the relationship (head of head, head, token) to the list
            relations.append((token.head.head, token.head, token))
    return relations    #list of relationships


# Function to build a knowledge graph from the given data
def build_knowledge_graph(data):
    G = nx.Graph()      # Initialize an empty graph using NetworkX
    
    for paragraph in data:      # Iterate through each paragraph in the data
        doc = nlp(paragraph)    # Process the paragraph using the spaCy model
        entities = extract_entities(paragraph)      # Extract entities from the paragraph
        relations = extract_relationships(doc)      # Extract relationships from the processed paragraph
        
        # Iterate through each entity and its label
        for entity, label in entities:      
            G.add_node(entity, label=label)     # Add the entity as a node in the graph with its label
        
        # Iterate through each relationship
        for subj, verb, obj in relations:
             # Add an edge between the subject and object nodes with the relationship as an attribute
            G.add_edge(subj.text, obj.text, relation=verb.lemma_)
    
    return G        #this is a constructed graph

# Function to read data from a CSV file
def read_data_from_csv(file_path):
    df = pd.read_csv(file_path)     #reading csv
    paragraphs = df['paragraphs'].dropna().tolist()     # Extract the 'paragraphs' column and convert it to a list, dropping any NA values
    return paragraphs

# Function to save the knowledge graph to a JSON file
def save_graph_to_json(graph, filename='graph.json'):
    # Convert graph nodes and edges to a dictionary format
    data = {
        'nodes': [{'id': node, 'label': data.get('label', 'No label')} for node, data in graph.nodes(data=True)],
        'edges': [{'source': u, 'target': v, 'relation': data.get('relation', 'No relation')} for u, v, data in graph.edges(data=True)]
    }
    # Open the specified file in write mode
    with open(filename, 'w') as f:
        # Dump the dictionary to the file as a JSON object
        json.dump(data, f, indent=2)

# Main execution block
if __name__ == "__main__":
    csv_file = input("Enter the CSV file path: ")
    paragraphs = read_data_from_csv(csv_file)
    G = build_knowledge_graph(paragraphs)       # Build the knowledge graph from the data
    
    print("Nodes:", G.nodes(data=True))
    print("Edges:", G.edges(data=True))

    # Save the graph to a JSON file
    save_graph_to_json(G, filename='knowledge_graph.json')
    print("Knowledge Graph saved to 'knowledge_graph.json'.")
