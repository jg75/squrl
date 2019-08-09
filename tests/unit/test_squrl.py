from datetime import datetime

from botocore.exceptions import ClientError
from botocore.stub import Stubber, ANY
from boto3 import client
import pytest

from squrl import Squrl


@pytest.fixture(scope="function")
def stubber(request):
    stub = Stubber(client("s3"))

    request.addfinalizer(stub.assert_no_pending_responses)

    return stub


@pytest.fixture(scope="session")
def parameters():
    bucket = "test-bucket"
    url = "test-url"
    key = Squrl.get_key(url)

    return {
        "bucket": bucket,
        "url": url,
        "key": key,
        "head_object": {"Bucket": bucket, "Key": key},
        "put_object": {
            "Bucket": bucket,
            "Key": key,
            "WebsiteRedirectLocation": url,
            "Expires": ANY,
            "ContentType": ANY,
        },
    }


def test_get_key(parameters):
    key = Squrl.get_key("test-url")

    assert len(key) == Squrl.key_length + 2
    assert key.startswith("u/")


def test_get_expiration(parameters):
    expiration = Squrl.get_expiration()

    assert expiration > datetime.now()


def test_key_exists(stubber, parameters):
    bucket = parameters["bucket"]
    key = parameters["key"]

    stubber.add_response("head_object", {}, expected_params=parameters["head_object"])
    stubber.activate()

    assert Squrl(bucket, client=stubber.client).key_exists(key)


def test_key_does_not_exist(stubber, parameters):
    bucket = parameters["bucket"]
    key = parameters["key"]

    stubber.add_client_error(
        "head_object",
        expected_params=parameters["head_object"],
        service_error_code="404",
    )
    stubber.activate()

    assert not Squrl(bucket, client=stubber.client).key_exists(key)


def test_key_error(stubber, parameters):
    bucket = parameters["bucket"]
    key = parameters["key"]

    stubber.add_client_error(
        "head_object",
        expected_params=parameters["head_object"],
        service_error_code="500",
    )
    stubber.activate()

    with pytest.raises(ClientError):
        Squrl(bucket, client=stubber.client).key_exists(key)


def test_get_method_key_exists(stubber, parameters):
    bucket = parameters["bucket"]
    url = parameters["url"]

    stubber.add_response("head_object", {}, expected_params=parameters["head_object"])
    stubber.activate()

    assert Squrl(bucket, client=stubber.client).get(url)


def test_get_method_key_does_not_exist(stubber, parameters):
    bucket = parameters["bucket"]
    url = parameters["url"]

    stubber.add_client_error(
        "head_object",
        expected_params=parameters["head_object"],
        service_error_code="404",
    )
    stubber.activate()

    assert not Squrl(bucket, client=stubber.client).get(url)


def test_create_method(stubber, parameters):
    bucket = parameters["bucket"]
    url = parameters["url"]

    stubber.add_response("put_object", {}, expected_params=parameters["put_object"])
    stubber.activate()

    assert Squrl(bucket, client=stubber.client).create(url)
