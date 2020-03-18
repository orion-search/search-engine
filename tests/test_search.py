import pytest
from unittest.mock import patch
import pickle

from utils import load_from_s3
from utils import read_pickle


@patch("utils.boto3")
def test_load_from_s3(boto3):
    load_from_s3("bucket", "filename")

    boto3.resource.assert_called_with("s3")
    boto3.resource().Object.assert_called_with("bucket", "filename")


def test_read_pickle():
    data = "foo"
    pkl = pickle.dumps(data)

    result = read_pickle(pkl)

    assert result == data
