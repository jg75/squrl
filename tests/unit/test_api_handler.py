from json import dumps
from unittest.mock import MagicMock

import pytest

from squrl import ApiHandler


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


def test_get_response_ok():
    response = "test-body"
    expected_response = {
        "statusCode": "200",
        "body": dumps(response),
        "headers": {
            "Content-Type": "application/json",
        },
    }
    actual_response = ApiHandler.get_response(response=response)

    assert expected_response == actual_response


def test_get_response_error():
    error = ValueError("test-error")
    expected_response = {
        "statusCode": "400",
        "body": str(error),
        "headers": {
            "Content-Type": "application/json",
        },
    }
    actual_response = ApiHandler.get_response(error=error)

    assert expected_response == actual_response


@pytest.mark.parametrize("method, url", [
    ("GET", "test-get"),
    ("POST", "test-post"),
    ("PUT", "test-put"),
    ("OTHER", "test-other")
])
def test_parse_event(event, method, url):
    event["httpMethod"] = method

    if method == "GET":
        event["queryStringParameters"] = dumps({"url": url})
    else:
        event["body"] = dumps({"url": url})

    method, body = ApiHandler.parse_event(event)

    assert method == method
    assert body["url"] == url


def test_call_handler(event, context):
    key = "response"
    mock_handler = MagicMock(return_value=key)
    api_handler = ApiHandler(mock_handler)
    response = api_handler(event, context)

    mock_handler.assert_called_once_with(event, context)
    assert response == key
