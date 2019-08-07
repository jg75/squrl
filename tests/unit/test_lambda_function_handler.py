from json import dumps
from unittest.mock import MagicMock

import pytest

from squrl import handler


@pytest.fixture(scope="function")
def event():
    return {}


@pytest.fixture(scope="function")
def context():
    return {}


@pytest.mark.parametrize("method, url, key", [
    ("GET", "https://get.example.com", "u/fake123"),
    ("POST", "https://post.example.com", "u/fake456"),
    ("PUT", "https://put.example.com", "u/fake789"),
    ("UNKNOWN", "https://unknown.example.com", "")
])
def test_handler(event, context, method, url, key):
    event["httpMethod"] = method

    if method == "GET":
        event["queryStringParameters"] = dumps({"url": url})
    else:
        event["body"] = dumps({"url": url})

    mock_method = MagicMock(return_value=key)
    registry = {
        "GET": mock_method,
        "POST": mock_method,
        "PUT": mock_method
    }

    response = handler(event, context, registry=registry)

    if method in registry.keys():
        mock_method.assert_called_once_with(url)
        assert response["statusCode"] == "200"
        assert isinstance(response["body"], str)
    else:
        mock_method.assert_not_called()
        assert response["statusCode"] == "400"
