from flask import Flask
from flask_restful import reqparse, abort, Api, Resource
from search import search_tfidf
import os
import faiss
from dotenv import load_dotenv, find_dotenv
from utils import load_from_s3, read_pickle

app = Flask(__name__)
api = Api(app)

# Parse arguments
parser = reqparse.RequestParser()
parser.add_argument("query")
parser.add_argument("results")


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
            "D": [float(elem) for elem in D[0]],
            "I": [float(elem) for elem in I[0]],
        }


# Setup the API resource routing here
# Route the URL to the resource
api.add_resource(VectorSimilarity, "/")

if __name__ == "__main__":

    # Get environmental variables
    load_dotenv(find_dotenv())
    s3_bucket = os.getenv("s3_bucket")
    tfidf_model = os.getenv("tfidf_model")
    svd_model = os.getenv("svd_model")
    faiss_index = os.getenv("faiss_index")

    # Load models from s3
    tfidf = read_pickle(load_from_s3(s3_bucket, tfidf_model))
    svd = read_pickle(load_from_s3(s3_bucket, svd_model))
    index = faiss.deserialize_index(read_pickle(load_from_s3(s3_bucket, faiss_index)))

    app.run(debug=True)
