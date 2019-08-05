from json import dumps
from unittest.mock import patch
from urllib.parse import quote_plus

from pytest import fixture

from squrl import Squrl, handler


@fixture(scope="function")
def patch_client():
    client = "squrl.lambda_function.Squrl.client"

    return patch(client, autospec=True)


@fixture(scope="session")
def url():
    return "https://fake.example.com"


@fixture(scope="session")
def head_object_response(url):
    return {"url": url, "key": Squrl.get_key(url)}


@fixture(scope="session")
def put_object_response():
    return {}


@fixture(scope="function")
def event(url):
    body = {"url": quote_plus(url)}
    return {"queryStringParameters": body}


@fixture(scope="function")
def context():
    return {}


def test_handle_unhandled_method(patch_client, event, context):
    event["httpMethod"] = "UNHANDLED_METHOD"
    response = handler(event, context)

    assert response["statusCode"] == "400"


def test_handle_get(patch_client, head_object_response, event, context):
    event["httpMethod"] = "GET"

    with patch_client as client:
        client.head_object.return_value = head_object_response
        response = handler(event, context)

        assert response["statusCode"] == "200"
        client.head_object.assert_called_once()


def test_handle_post(patch_client, put_object_response, event, context):
    event["httpMethod"] = "POST"
    event["body"] = dumps({"url": quote_plus("https://post.example.com")})

    with patch_client as client:
        client.put_object.return_value = put_object_response
        response = handler(event, context)

        assert response["statusCode"] == "200"
        client.put_object.assert_called_once()


def test_handle_put(patch_client, put_object_response, event, context):
    event["httpMethod"] = "PUT"
    event["body"] = dumps({"url": quote_plus("https://put.example.com")})

    with patch_client as client:
        client.put_object.return_value = put_object_response
        response = handler(event, context)

        assert response["statusCode"] == "200"
        client.put_object.assert_called_once()
