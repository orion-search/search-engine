import pytest
from unittest.mock import patch
import pickle
from pytest_elasticsearch import factories

from utils import load_from_s3
from utils import read_pickle
from search import es_search


@patch("utils.boto3")
def test_load_from_s3(boto3):
    load_from_s3("bucket", "filename")

    boto3.resource().Object.assert_called_with("bucket", "filename")


# TODO: Change the path of this executable when running on docker
elasticsearch_proc = factories.elasticsearch_proc(
    executable="/Users/kstathou/Desktop/elastic/elasticsearch-7.5.0/bin/elasticsearch",
    port=-1,
    index_store_type="fs",
)
elasticsearch = factories.elasticsearch("elasticsearch_proc")


class TestSuccessResponses:
    @pytest.fixture(autouse=True)
    def spam_index(self, elasticsearch):
        elasticsearch.indices.create(index="spam")
        elasticsearch.indices.put_mapping(
            {
                "properties": {
                    "abstract": {"type": "text", "analyzer": "standard"},
                    "abstract_suggest": {
                        "type": "text",
                        "fields": {"keyword": {"type": "keyword", "ignore_above": 256}},
                    },
                    "author": {
                        "properties": {
                            "affiliation": {
                                "type": "text",
                                "fields": {
                                    "keyword": {"type": "keyword", "ignore_above": 256}
                                },
                            },
                            "name": {
                                "type": "text",
                                "fields": {
                                    "keyword": {"type": "keyword", "ignore_above": 256}
                                },
                            },
                        }
                    },
                    "authors": {
                        "type": "nested",
                        "properties": {
                            "affiliation": {
                                "type": "text",
                                "fields": {"raw": {"type": "keyword"}},
                            },
                            "name": {
                                "type": "text",
                                "fields": {"raw": {"type": "keyword"}},
                            },
                        },
                    },
                    "citations": {"type": "integer"},
                    "fields_of_study": {
                        "type": "nested",
                        "include_in_parent": True,
                        "properties": {
                            "id": {"type": "long"},
                            "name": {
                                "type": "text",
                                "fields": {"raw": {"type": "keyword"}},
                            },
                        },
                    },
                    "original_title": {"type": "text", "analyzer": "standard"},
                    "original_title_suggest": {
                        "type": "text",
                        "fields": {"keyword": {"type": "keyword", "ignore_above": 256}},
                    },
                    "publication_date": {"type": "date"},
                    "year": {"type": "keyword"},
                }
            },
            index="spam",
        )

    def test_es_search(self, elasticsearch):
        elasticsearch.create(
            "spam",
            "123",
            {
                "year": 2020,
                "publication_date": "2020-03-06",
                "original_title": "Improved stability of an engineered function using adapted bacterial strains",
                "abstract": "Engineering useful functions into cells is one of the primary goals of synthetic biology. However, engineering novel functions that remain stable for multiple generations remains a significant challenge. Here we report the importance of host fitness on the stability of an engineered function. We find that the initial fitness of the host cell affects the stability of the engineered function. We demonstrate that adapting a strain to the intended growth condition increases fitness and in turn improves the stability of the engineered function over hundreds of generations. This approach offers a simple and effective method to increase the stability of engineered functions without genomic modification or additional engineering and will be useful in improving the stability of novel, engineered functions in living cells.",
                "citations": "0",
                "original_title_suggest": "Improved stability of an engineered function using adapted bacterial strains",
                "abstract_suggest": "Engineering useful functions into cells is one of the primary goals of synthetic biology. However, engineering novel functions that remain stable for multiple generations remains a significant challenge. Here we report the importance of host fitness on the stability of an engineered function. We find that the initial fitness of the host cell affects the stability of the engineered function. We demonstrate that adapting a strain to the intended growth condition increases fitness and in turn improves the stability of the engineered function over hundreds of generations. This approach offers a simple and effective method to increase the stability of engineered functions without genomic modification or additional engineering and will be useful in improving the stability of novel, engineered functions in living cells.",
                "fields_of_study": [
                    {"name": "Biology", "id": 86803240},
                    {"name": "Genetics", "id": 54355233},
                    {"name": "Computational biology", "id": 70721500},
                    {"name": "Synthetic biology", "id": 191908910},
                ],
                "author": [
                    {
                        "name": "Vanya Paralanov",
                        "affiliation": "national institute of standards and technology",
                    },
                    {
                        "name": "Peter D. Tonner",
                        "affiliation": "national institute of standards and technology",
                    },
                    {
                        "name": "Elena Musteata",
                        "affiliation": "national institute of standards and technology",
                    },
                    {
                        "name": "David Ross",
                        "affiliation": "national institute of standards and technology",
                    },
                    {
                        "name": "Drew S Tack",
                        "affiliation": "national institute of standards and technology",
                    },
                ],
            },
            refresh=True,
        )

        results = es_search(query="stability", index="spam", client=elasticsearch)
        assert results.hits.total["value"] == 1
        assert [hit.meta.id for hit in results] == ["123"]
