def search_tfidf(query, tfidf, svd, index, num_results=10):
    vector = tfidf.transform(query)
    vector = svd.transform(vector)

    D, I = index.search(vector.astype("float32"), k=num_results)
    return D, I
