FROM continuumio/miniconda3

WORKDIR /api

ADD environment.yml /tmp/environment.yml
RUN conda env create -f /tmp/environment.yml

# Make RUN commands use the new environment
SHELL ["conda", "run", "-n", "myenv", "/bin/bash", "-c"]

# Install curl
RUN apt-get update && apt-get install -y \
curl

# RUN echo "source activate env" > ~/.bashrc
# ENV PATH /opt/conda/envs/env/bin:$PATH

COPY *.py ./
COPY .env ./

# Expose port
EXPOSE 5000

# Change to virtual env and start the app
ENTRYPOINT ["conda", "run", "-n", "myenv", "gunicorn", "--bind", "0.0.0.0:5000", "wsgi:app", "--timeout", "140"]
