from flask import Flask, request, jsonify
import KnowledgeGraphConstruction as kgc 
#import build_knowledge_graph, save_graph_to_json, read_data_from_csv
import os

app = Flask(__name__)

@app.route('/generate-graph', methods=['POST'])
def generate_graph():
    # Get file path from request
    file_path = request.json.get('file_path')
    if not file_path:
        return jsonify({'error': 'File path is required'}), 400

    if not os.path.isfile(file_path):
        return jsonify({'error': 'File does not exist'}), 400

    # Read data from CSV, build graph, and save to JSON
    paragraphs = kgc.read_data_from_csv(file_path)
    graph = kgc.build_knowledge_graph(paragraphs)
    kgc.save_graph_to_json(graph, filename='knowledge_graph.json')

    return jsonify({'message': 'Knowledge graph generated successfully'}), 200

if __name__ == "__main__":
    app.run(debug=True)
