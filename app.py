from flask import Flask, request, jsonify, make_response
from flask_cors import CORS, cross_origin
import networkx as nx
from networkx.readwrite import json_graph
import json

# Initialize a Flask application
app = Flask(__name__)
# Enable Cross-Origin Resource Sharing (CORS) for the app
CORS(app)

# Load the graph from the JSON file
try:
    with open('knowledge_graph.json') as f:
        graph_data = json.load(f)
        print("JSON file loaded successfully.")
except Exception as e:
    print(f"Failed to load JSON file: {e}")

# Convert JSON data to NetworkX graph
def load_graph_from_json(data):
    G = nx.Graph()      # Create an empty graph
    try:
        # Add nodes with labels to the graph
        for node in data['nodes']:
            G.add_node(node['id'], label=node['label'])
        # Add edges with relationships to the graph
        for edge in data['edges']:
            G.add_edge(edge['source'], edge['target'], relation=edge['relation'])
        print("Graph loaded from JSON successfully.")
    except Exception as e:
        print(f"Error loading graph from JSON: {e}")
    return G

# Load the graph from the JSON data
G = load_graph_from_json(graph_data)

# Route to get the graph data as JSON
@app.route('/api/data', methods=['GET'])
def get_data():
    try:
        # Convert the NetworkX graph to a JSON-serializable format
        graph_data = json_graph.node_link_data(G)
        response = make_response(json.dumps(graph_data))
        response.headers['Content-Type'] = 'application/json'
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    except Exception as e:
        print(f"Error in /api/data route: {e}")
        return jsonify({"error": "Failed to get data"}), 200

# Route to query the graph
@app.route('/query', methods=['OPTIONS', 'POST', 'GET'])
@cross_origin()
def query_graph():
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response

    if request.method == 'POST':
        try:
            # Get the query data from the POST request
            query_data = request.json
            query = query_data.get('query', '').strip().lower()
            print(f"Received query: {query}")

            if not query:
                response = {"answer": "No query provided. Please provide a query."}
            else:
                # Query for specific node information
                if query.startswith("info about") or query.startswith("information about"):
                    node = query.split("about")[-1].strip()
                    print("In loop startwith node")
                    if G.has_node(node):
                        node_data = G.nodes[node]
                        response = {
                            "answer": f"Node '{node}' has label '{node_data.get('label', 'unknown')}'."
                        }
                    else:
                        matches = []
                    
                        for u, v, data in G.edges(data=True):
                            if node in u.lower() or node in v.lower() or node in data.get('relation', '').lower():
                                matches.append(f"{u} -- {v}: {data.get('relation', 'unknown')}")
                        print(matches)
                        if matches:
                            response = {
                                "answer": f"Found matches: {', '.join(matches)}."
                            }
                        else:
                            response = {
                                "answer": "No matches found for the query."
                            }
                        
                # Query for edges related to a specific node
                elif query.startswith("relationships of") or query.startswith("relations of"):
                    node = query.split("of")[-1].strip()
                    print("In loop startwith edge")
                    if G.has_node(node):
                        edges = list(G.edges(node, data=True))
                        if edges:
                            relations = [f"{u} -- {v}: {data.get('relation', 'unknown')}" for u, v, data in edges]
                            response = {
                                "answer": f"Node '{node}' has the following relationships: {', '.join(relations)}."
                            }
                    else:
                        matches = []
                        for u, v, data in G.edges(data=True):
                            if node in u.lower() or node in v.lower() or node in data.get('relation', '').lower():
                                matches.append(f"{u} -- {v}: {data.get('relation', 'unknown')}")

                        if matches:
                            response = {
                                "answer": f"Found matches: {', '.join(matches)}."
                            }
                        else:
                            response = {
                                "answer": "No matches found for the query."
                            }

                # General query to find any mentions of a keyword
                else:
                    matches = []
                    print("In loop keyword")
                    for u, v, data in G.edges(data=True):
                        if query in u.lower() or query in v.lower() or query in data.get('relation', '').lower():
                            matches.append(f"{u} -- {v}: {data.get('relation', 'unknown')}")

                    if matches:
                        response = {
                            "answer": f"Found matches: {', '.join(matches)}."
                        }
                    else:
                        response = {
                            "answer": "No matches found for the query."
                        }

            print(f"Response: {response}")
            return jsonify(response)

        except Exception as e:
            print(f"Error in /query route: {e}")
            response = {"error": str(e)}
            return jsonify(response), 200

    if request.method == 'GET':
        data = {'message': 'Hello, CORS! GET request handled.'}
        return jsonify(data)

# Route to download the query response as a text file
@app.route('/download', methods=['POST'])
@cross_origin()
def download_response():
    try:
        # Get the response data from the POST request
        response_data = request.json.get('response', '')
        if not response_data:
            return jsonify({"error": "No response data provided"}), 400

        # Create a response with the data to be downloaded
        response = make_response(response_data)
        response.headers["Content-Disposition"] = "attachment; filename=response.txt"
        response.headers["Content-Type"] = "text/plain"
        return response
    except Exception as e:
        print(f"Error in /download route: {e}")
        return jsonify({"error": str(e)}), 500

# Run the Flask application
if __name__ == '__main__':
    app.run(debug=True)
