from flask import Flask
from flask_restful import reqparse, abort, Api, Resource
from flask_restful.utils import cors
from utils import load_from_s3, read_pickle, aws_es_client
from search import search_tfidf, es_search

# from elasticsearch import Elasticsearch
from dotenv import load_dotenv, find_dotenv

import os
import faiss

app = Flask(__name__)
api = Api(app)

# Parse arguments
parser = reqparse.RequestParser()
parser.add_argument("query")
parser.add_argument("results")
parser.add_argument("citation_count")

# VectorSimilarity models
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
    faiss_index = faiss.deserialize_index(read_pickle(f))

# ES client
load_dotenv(find_dotenv())

es_port = os.getenv("es_port")
es_host = os.getenv("es_host")
region = os.getenv("region")
es_index = os.getenv("es_index")
es = aws_es_client(es_host, es_port, region)


class VectorSimilarity(Resource):
    @cors.crossdomain(origin="*")
    def get(self):
        # Parse user's query
        args = parser.parse_args()
        user_query = args["query"]
        num_results = args["results"]

        # Find relevant documents
        D, I = search_tfidf([user_query], tfidf, svd, faiss_index, int(num_results))

        # Create JSON response
        return {
            "D": D.flatten().tolist(),
            "I": I.flatten().tolist(),
        }


class ElasticsearchSearch(Resource):
    @cors.crossdomain(origin="*")
    def get(self):
        # Parse user's query
        args = parser.parse_args()
        user_query = args["query"]
        num_results = args["results"]
        citation_count = args["citation_count"]

        # Query ES and return paper IDs and ranking score
        response = es_search(
            query=user_query,
            index=es_index,
            client=es,
            citations=citation_count,
            size=int(num_results),
        )
        return {
            "I": [hit.meta.id for hit in response],
            "S": [hit.meta.score for hit in response],
        }


# Route the URL to the resource
api.add_resource(VectorSimilarity, "/vector-search")
api.add_resource(ElasticsearchSearch, "/keyword-search")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
