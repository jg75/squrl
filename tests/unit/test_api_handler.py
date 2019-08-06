from json import dumps

import pytest

from squrl import ApiHandler


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


@pytest.mark.parametrize("method, url, should_pass", [
    ("GET", "test-get", True),
    ("POST", "test-post", True),
    ("PUT", "test-put", True),
    ("UNHANDLED", "test-error", False)
])
def test_parse_event(method, url, should_pass):
    event = {"httpMethod": method}

    if method == "GET":
        event["queryStringParameters"] = dumps({"url": url})
    else:
        event["body"] = dumps({"url": url})

    if should_pass:
        method, body = ApiHandler().parse_event(event)

        assert method == method
        assert body["url"] == url
    else:
        with pytest.raises(ValueError):
            method, body = ApiHandler().parse_event(event)
