# Start with a base image
FROM python:3-onbuild

# Copy our application code
WORKDIR .
COPY . .
COPY requirements.txt .
COPY .env .

# Fetch app specific dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expose port
EXPOSE 5000

# Start the app
# CMD ["python", "api.py", "--host", "0.0.0.0"]
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "wsgi:app", "--timeout", "140"]
