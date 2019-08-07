from json import dumps
from unittest.mock import MagicMock

import pytest

from squrl import handler


@pytest.fixture(scope="function")
def event():
    return {
        "httpMethod": "UNKNOWN",
        "queryStringParameters": "{}",
        "body": "{}"
    }


@pytest.fixture(scope="function")
def context():
    return {}


@pytest.mark.parametrize("method, url, key", [
    ("GET", "https://get.example.com", "u/fake123"),
    ("POST", "https://post.example.com", "u/fake456"),
    ("POST", "https://put.example.com", "u/fake789")
])
def test_handler(event, context, method, url, key):
    event["httpMethod"] = method

    if method == "GET":
        event["queryStringParameters"] = dumps({"url": url})
    else:
        event["body"] = dumps({"url": url})

    mock_method = MagicMock(return_value=key)
    registry = {method: mock_method}
    response = handler(event, context, registry=registry)

    mock_method.assert_called_once_with(url)
    assert response["statusCode"] == "200"
    assert isinstance(response["body"], str)


def test_handler_error(event, context):
    with pytest.raises(ValueError):
        handler(event, context)
