import datetime
import json

import boto3
from botocore.stub import Stubber, ANY
from pytest import fixture

from squrl import Squrl


@fixture(scope="function")
def stubber(request):
    client = boto3.client("s3")
    stub = Stubber(client)

    request.addfinalizer(stub.assert_no_pending_responses)

    return stub


def test_get_key():
    key = Squrl.get_key("test-url")

    assert len(key) == Squrl.key_length + 2
    assert key.startswith("u/")


def test_get_expiration():
    expiration = Squrl.get_expiration()

    assert expiration > datetime.datetime.now()


def test_key_exists(stubber):
    expected_params = {
        "Bucket": ANY,
        "Key": ANY
    }

    stubber.add_response(
        "head_object", {}, expected_params=expected_params
    )
    stubber.activate()

    assert Squrl(stubber.client, "test-bucket").key_exists("test-key")


def test_key_does_not_exist(stubber):
    expected_params = {
        "Bucket": ANY,
        "Key": ANY
    }

    stubber.add_client_error(
        "head_object",
        expected_params=expected_params,
        service_error_code="404"
    )
    stubber.activate()

    assert not Squrl(stubber.client, "test-bucket").key_exists("test-key")


def test_get_response_ok():
    response = "test-body"
    expected_response = {
        "statusCode": "200",
        "body": json.dumps(response),
        "headers": {
            "Content-Type": "application/json",
        },
    }
    actual_response = Squrl.get_response(response=response)

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
    actual_response = Squrl.get_response(error=error)

    assert expected_response == actual_response


def test_get_method_key_exists(stubber):
    expected_params = {
        "Bucket": ANY,
        "Key": ANY
    }

    stubber.add_response(
        "head_object", {}, expected_params=expected_params
    )
    stubber.activate()

    squrl = Squrl(stubber.client, "test-bucket")

    assert squrl.registry["GET"]("test-url")


def test_get_method_key_does_not_exist(stubber):
    expected_params = {
        "Bucket": ANY,
        "Key": ANY
    }

    stubber.add_client_error(
        "head_object",
        expected_params=expected_params,
        service_error_code="404"
    )
    stubber.activate()

    squrl = Squrl(stubber.client, "test-bucket")

    assert not squrl.registry["GET"]("test-url")


def test_post_method(stubber):
    method = "POST"
    bucket = "test-bucket"
    url = "test-url"
    key = Squrl.get_key(url)
    expected_params = {
        "Bucket": bucket,
        "Key": key,
        "WebsiteRedirectLocation": url,
        "Expires": ANY,
        "ContentType": ANY
    }

    stubber.add_response(
        "put_object", {}, expected_params=expected_params
    )
    stubber.activate()

    squrl = Squrl(stubber.client, bucket)

    assert squrl.registry[method](url)


def test_put_method(stubber):
    method = "PUT"
    bucket = "test-bucket"
    url = "test-url"
    key = Squrl.get_key(url)
    expected_params = {
        "Bucket": bucket,
        "Key": key,
        "WebsiteRedirectLocation": url,
        "Expires": ANY,
        "ContentType": ANY
    }

    stubber.add_response(
        "put_object", {}, expected_params=expected_params
    )
    stubber.activate()

    squrl = Squrl(stubber.client, bucket)

    assert squrl.registry[method](url)
