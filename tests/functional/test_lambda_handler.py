from json import dumps
from unittest.mock import MagicMock

import pytest

from squrl import ApiHandler


@pytest.fixture(scope="function")
def event():
    return {"httpMethod": "UNHANDLED_METHOD"}


@pytest.fixture(scope="function")
def context():
    return {}


def test_unhandled_method(event, context):
    event["httpMethod"] = "UNHANDLED_METHOD"

    with pytest.raises(ValueError):
        ApiHandler().handler(event, context)


@pytest.mark.parametrize("method, url, key", [
    ("GET", "https://get.example.com", "u/fake123"),
    ("POST", "https://post.example.com", "u/fake456"),
    ("POST", "https://put.example.com", "u/fake789"),
])
def test_handler(event, context, method, url, key):
    event["httpMethod"] = method

    if method == "GET":
        event["queryStringParameters"] = dumps({"url": url})
    else:
        event["body"] = dumps({"url": url})

    mock_method = MagicMock(return_value=key)
    api_handler = ApiHandler()
    api_handler.registry[method] = mock_method
    response = api_handler.handler(event, context)

    mock_method.assert_called_once_with(url)
    assert response["statusCode"] == "200"
    assert isinstance(response["body"], str)
