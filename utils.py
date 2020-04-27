import boto3
import pickle
from dotenv import load_dotenv, find_dotenv
import os
from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth

load_dotenv(find_dotenv())


def load_from_s3(bucket, prefix):
    """Loads a pickled file from s3.

    Args:
       bucket (str): Name of the s3 bucket.
       prefix (str): Name of the pickled file.

    """
    s3 = boto3.resource(
        "s3",
        aws_access_key_id=os.getenv("aws_access_key_id"),
        aws_secret_access_key=os.getenv("aws_secret_access_key"),
    )
    obj = s3.Object(bucket, f"{prefix}.pickle")
    return pickle.loads(obj.get()["Body"].read())

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
    awsauth = AWS4Auth(
        os.getenv("aws_access_key_id"),
        os.getenv("aws_secret_access_key"),
        os.getenv("region"),
        "es",
    )

    es = Elasticsearch(
        hosts=[{"host": host, "port": port}],
        http_auth=awsauth,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection,
    )

    return es
