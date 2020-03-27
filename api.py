from flask import Flask
from flask_restful import reqparse, abort, Api, Resource
from utils import load_from_s3, read_pickle
from search import search_tfidf

import os
import faiss

app = Flask(__name__)
api = Api(app)

# Parse arguments
parser = reqparse.RequestParser()
parser.add_argument("query")
parser.add_argument("results")

with open(
    os.path.join(os.path.dirname(__file__), "models/tfidf_model.pickle"), "rb"
) as f:
    tfidf = read_pickle(f)

with open(
    os.path.join(os.path.dirname(__file__), "models/svd_model.pickle"), "rb"
) as f:
    svd = read_pickle(f)

with open(
    os.path.join(os.path.dirname(__file__), "models/faiss_index.pickle"), "rb"
) as f:
    index = faiss.deserialize_index(read_pickle(f))


class VectorSimilarity(Resource):
    def get(self):
        # Parse user's query
        args = parser.parse_args()
        user_query = args["query"]
        num_results = args["results"]

        # Find relevant documents
        D, I = search_tfidf([user_query], tfidf, svd, index, int(num_results))

        # Create JSON response
        return {
            "D": D.flatten().tolist(),
            "I": I.flatten().tolist(),
        }


# Setup the API resource routing here
# Route the URL to the resource
api.add_resource(VectorSimilarity, "/")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
