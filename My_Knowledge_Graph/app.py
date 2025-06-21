from flask import Flask, request, jsonify, make_response
from flask_cors import CORS,cross_origin
import networkx as nx
from networkx.readwrite import json_graph
import json

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

# Configure CORS
CORS(app, resources={r"/*": {"origins": "*"}})  # Allow all origins for all routes
#CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})


# Load the graph from the JSON file
with open('knowledge_graph.json') as f:
    print("in json")
    graph_data = json.load(f)


# Convert JSON data to NetworkX graph
def load_graph_from_json(data):
    print("in load_graph")
    # Assume G is your NetworkX graph object created elsewhere in your code
    G = nx.Graph()
    for node in data['nodes']:
        G.add_node(node['id'], label=node['label'])
    for edge in data['edges']:
        G.add_edge(edge['source'], edge['target'], relation=edge['relation'])
    return G

G = load_graph_from_json(graph_data)

@app.route('/api/data', methods=['GET'])
def get_data():
    #data = {'message': 'Hello, CORS!'}
    #data = load_graph_from_json(G)
    #response = jsonify(G)
    graph_data = json_graph.node_link_data(G)
    response = make_response(json.dumps(graph_data))
    response.headers['Content-Type'] = 'application/json'
    response.headers.add('Access-Control-Allow-Origin', '*') # Allow requests from any origin
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS') # Allow these HTTP methods
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type') # Allow these headers
    return response

@app.route('/query', methods=['OPTIONS', 'POST','GET'])

@cross_origin()

def query_graph():
    if request.method == 'OPTIONS':
        response = app.make_default_options_response()
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response 
    
    elif request.method == 'POST':
        #data = request.load_graph_from_json(graph_data)
        data = {'message': 'Hello, CORS!'} 
        print("-------------G",G)

        try:
        # Convert the NetworkX graph to a JSON-serializable format
            graph_data = json_graph.node_link_data(G)
            response = make_response(json.dumps(graph_data))
            response.headers['Content-Type'] = 'application/json'
            return response
        except Exception as e:
            response = make_response(json.dumps({'error': str(e)}))
            response.headers['Content-Type'] = 'application/json'
            return response, 500

        #response = jsonify(G)
        #print("response_________________",response)
        # Process data as needed
        #return response
        #return jsonify(G), 200 
        # Return HTTP 200 OK status for POST request 
          
    elif request.method == 'GET':
        data = {'message': 'Hello, CORS! GET request handled.'}
        return jsonify(data)

    query = request.json.get('query', '').strip().lower()
    response = {"answer": "Sorry, I didn't understand the query."}

    if not query:
        response = {"answer": "No query provided. Please provide a query."}
    else:
        # Query for specific node information
        if query.startswith("info about") or query.startswith("information about"):
            node = query.split("about")[-1].strip()
            if G.has_node(node):
                node_data = G.nodes[node]
                response = {
                    "answer": f"Node '{node}' has label '{node_data.get('label', 'unknown')}'."
                }
            else:
                response = {
                    "answer": f"Node '{node}' not found in the knowledge graph."
                }
        
        # Query for edges related to a specific node
        elif query.startswith("relationships of") or query.startswith("relations of"):
            node = query.split("of")[-1].strip()
            if G.has_node(node):
                edges = list(G.edges(node, data=True))
                if edges:
                    relations = [f"{u} -- {v}: {data.get('relation', 'unknown')}" for u, v, data in edges]
                    response = {
                        "answer": f"Node '{node}' has the following relationships: {', '.join(relations)}."
                    }
                else:
                    response = {
                        "answer": f"Node '{node}' has no relationships in the knowledge graph."
                    }
            else:
                response = {
                    "answer": f"Node '{node}' not found in the knowledge graph."
                }
        
        # General query to find any mentions of a keyword
        else:
            matches = []
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
    
    return jsonify(response)

'''### CORS section
    @app.after_request
    def after_request_func(response):
        origin = request.headers.get('Origin')
        if request.method == 'OPTIONS':
            response = make_response()
            response.headers.add('Access-Control-Allow-Credentials', 'true')
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
            response.headers.add('Access-Control-Allow-Headers', 'x-csrf-token')
            response.headers.add('Access-Control-Allow-Methods',
                                'GET, POST, OPTIONS, PUT, PATCH, DELETE')
            if origin:
                response.headers.add('Access-Control-Allow-Origin', origin)
        else:
            response.headers.add('Access-Control-Allow-Credentials', 'true')
            if origin:
                response.headers.add('Access-Control-Allow-Origin', origin)

        return response
    ### end CORS section'''

if __name__ == '__main__':
    app.run(debug=True)
    #app.run(host='0.0.0.0', port=500)
