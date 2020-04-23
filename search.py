from elasticsearch_dsl import Search, Q


def search_tfidf(query, tfidf, svd, index, num_results=10):
    """Finds similar TF-IDF vectors using FAISS index.

    Args:
        query (str): User query that should be more than a sentence long.
        tfidf (`sklearn.feature_extraction.text.TfidfVectorizer`): Fitted 
            TF-IDF model. Transforms the user query to vector.
        svd (`sklearn.decomposition._truncated_svd.TruncatedSVD`): Fitted 
            SVD model that reduced the dimensionality of the TF-IDF vectors.
        index (`numpy.ndarray`): FAISS index that needs to be deserialized.
        num_results (int): Number of results to return.

    Returns:
        D (:obj:`numpy.array` of `float`): Distance between results and query.
        I (:obj:`numpy.array` of `int`): Paper ID of the results.

    """
    vector = tfidf.transform(query)
    vector = svd.transform(vector)

    D, I = index.search(vector.astype("float32"), k=num_results)
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
