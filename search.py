import torch
from elasticsearch_dsl import Search, Q
import numpy as np


def vector_search(query, model, index, num_results=10):
    """Tranforms query to vector using a pretrained, sentence-level 
    DistilBERT model and finds similar vectors using FAISS.

    Args:
        query (str): User query that should be more than a sentence long.
        model (sentence_transformers.SentenceTransformer.SentenceTransformer)
        index (`numpy.ndarray`): FAISS index that needs to be deserialized.
        num_results (int): Number of results to return.

    Returns:
        D (:obj:`numpy.array` of `float`): Distance between results and query.
        I (:obj:`numpy.array` of `int`): Paper ID of the results.
    
    """
    vector = model.encode(query)
    D, I = index.search(np.array(vector).astype("float32"), k=num_results)
    return D, I


def es_search(
    query,
    index,
    client,
    fields=["original_title", "abstract", "fields_of_study.name"],
    citations=0,
    size=10,
):
    """Performs an Elasticsearch query.

    Args:
        index (str): Name of the ES index to query.
        client (str): ES client.
        query (str): User query that should be a keyword or short phrase.
        fields (:obj:`list` of `str`): ES index fields to be used in search.
            Defaults to abstract, title and fields of study.
        citations (int): Filter results by citation count.
        size (int): Number of returned results.

    Returns:
        (`elasticsearch_dsl.response.Response`): ES response.

    """
    s = Search(index=index).using(client)
    # Multi-match query
    s = s.query(Q("multi_match", query=query, fields=fields))
    # Keep results with a citation count "greater than or equal"
    s = s.filter("range", citations={"gte": citations})
    # Slice response
    s = s[:size]
    return s.execute()
