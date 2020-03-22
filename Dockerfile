# Start with a base image
FROM python:3-onbuild
# FROM python:alpine3.7

# Copy our application code
WORKDIR /api

COPY requirements.txt .
COPY models/ ./models
COPY *.py ./

# Fetch app specific dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expose port
EXPOSE 5000

# Start the app
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "wsgi:app", "--timeout", "140"]
