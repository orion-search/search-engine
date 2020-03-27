import boto3
import pickle
from dotenv import load_dotenv, find_dotenv
import os

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
