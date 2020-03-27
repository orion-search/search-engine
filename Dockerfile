# Start with a base image
FROM python:3-onbuild as base
# FROM python:alpine3.7

FROM base as builder

WORKDIR /install
COPY requirements.txt /requirements.txt

# Fetch app specific dependencies
RUN pip install --upgrade pip
RUN pip install --install-option="--prefix=/install" -r /requirements.txt

FROM base

# Copy our application code
WORKDIR /api

COPY --from=builder /install /usr/local
COPY *.py ./
# COPY models/ ./models
RUN mkdir -p /api/models \
  && curl -o /api/models/faiss_index.pickle https://document-vectors.s3.eu-west-2.amazonaws.com/faiss_index.pickle \
  && curl -o /api/models/svd_model.pickle https://document-vectors.s3.eu-west-2.amazonaws.com/svd_model.pickle \
  && curl -o /api/models/tfidf_model.pickle https://document-vectors.s3.eu-west-2.amazonaws.com/tfidf_model.pickle

# Expose port
EXPOSE 5000

# Start the app
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "wsgi:app", "--timeout", "140"]
