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


@pytest.fixture(scope="function")
def handlers():
    key = "u/fake123"
    mock_method = MagicMock(return_value=key)
    registry = {
        "GET": mock_method,
        "POST": mock_method,
        "PUT": mock_method
    }

    return {
        "key": key,
        "handler": mock_method,
        "registry": registry
    }


@pytest.mark.parametrize("method, url, key", [
    ("GET", "https://get.example.com", "u/fake123"),
    ("POST", "https://post.example.com", "u/fake456"),
    ("PUT", "https://put.example.com", "u/fake789"),
    ("DELETE", "https://delete.example.com", "u/fake789"),
    ("OPTIONS", "https://options.example.com", "u/fake789"),
    ("HEAD", "https://head.example.com", "u/fake789"),
    ("ANY", "https://head.example.com", "u/fake789"),
    ("UNKNOWN", "https://unknown.example.com", ""),
    ("", "", ""),
    (None, None, None),
])
def test_handler(event, context, handlers, method, url, key):
    event["httpMethod"] = method

    if method == "GET":
        event["queryStringParameters"] = dumps({"url": url})
    else:
        event["body"] = dumps({"url": url})

    response = handler(event, context, registry=handlers["registry"])

    if method in handlers["registry"].keys():
        handlers["handler"].assert_called_once_with(url)
        assert response["statusCode"] == "200"
        assert isinstance(response["body"], str)
    else:
        handlers["handler"].assert_not_called()
        assert response["statusCode"] == "400"
