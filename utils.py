import boto3
import pickle
from dotenv import load_dotenv, find_dotenv
import os
from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth

load_dotenv(find_dotenv())


def load_from_s3(bucket, filename):
    """Get an object from S3.
    
    Args:
        bucket (str): S3 bucket.
        filename (str): Name of the model file.
    
    Returns:
        (bytes)
    
    """
    s3 = boto3.resource(
        "s3",
        aws_access_key_id=os.getenv("aws_access_key_id"),
        aws_secret_access_key=os.getenv("aws_secret_access_key"),
    )
    obj = s3.Object(bucket, filename)
    return obj.get()["Body"].read()


def read_pickle(filename):
    """Read a pickle file."""
    # return pickle.loads(filename)
    return pickle.load(filename)


def aws_es_client(host, port, region):
    """Create a client with IAM based authentication on AWS.
    Boto3 will fetch the AWS credentials.

    Args:
        host (str): AWS ES domain.
        port (int): AWS ES port (default: 443).
        region (str): AWS ES region.

    Returns:
        es (elasticsearch.client.Elasticsearch): Authenticated AWS client.

    """
    # Get credentials
    # credentials = boto3.Session().get_credentials()
    awsauth = AWS4Auth(os.getenv("aws_access_key_id"), os.getenv("aws_secret_access_key"), os.getenv('region'), "es")

    es = Elasticsearch(
        hosts=[{"host": host, "port": port}],
        http_auth=awsauth,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection,
    )

    return es
