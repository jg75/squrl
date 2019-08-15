from json import dumps
from urllib.parse import quote

from boto3 import client
from botocore.stub import Stubber, ANY
import pytest

from squrl import ApiHandler, Squrl, handler


@pytest.fixture(scope="function")
def stubber(request):
    stub = Stubber(client("s3"))

    request.addfinalizer(stub.assert_no_pending_responses)

    return stub


@pytest.fixture(scope="function")
def bucket():
    return "test-bucket"


@pytest.fixture(scope="function")
def url():
    return "https://fake.example.com"


@pytest.fixture(scope="function")
def get_event(url):
    return {"httpMethod": "GET", "queryStringParameters": dumps({"url": quote(url)})}


@pytest.fixture(scope="function")
def post_event(url):
    return {"httpMethod": "POST", "body": dumps({"url": url})}


@pytest.fixture(scope="function")
def put_event(url):
    return {"httpMethod": "PUT", "body": dumps({"url": url})}


@pytest.fixture(scope="function")
def unsupported_event(url):
    return {"httpMethod": "UNSUPPORTED", "body": dumps({"url": url})}


@pytest.fixture(scope="function")
def context():
    return {}


@pytest.fixture(scope="function")
def squrl_get(bucket, stubber):
    stubber.add_response("head_object", {}, expected_params={"Bucket": ANY, "Key": ANY})
    stubber.activate()

    return Squrl(bucket, client=stubber.client)


@pytest.fixture(scope="function")
def squrl_create(bucket, stubber, url):
    stubber.add_response(
        "put_object",
        {},
        expected_params={
            "Bucket": ANY,
            "Key": ANY,
            "WebsiteRedirectLocation": url,
            "Expires": ANY,
            "ContentType": ANY,
        },
    )
    stubber.activate()

    return Squrl(bucket, client=stubber.client)


def test_handler_get(get_event, context, squrl_get):
    api_handler = ApiHandler(handler)
    response = api_handler(get_event, context, squrl=squrl_get)

    assert response["statusCode"] == "200"


def test_handler_post(post_event, context, squrl_create):
    api_handler = ApiHandler(handler)
    response = api_handler(post_event, context, squrl=squrl_create)

    assert response["statusCode"] == "200"


def test_handler_error(unsupported_event, context):
    api_handler = ApiHandler(handler)
    response = api_handler(unsupported_event, context)

    assert response["statusCode"] == "400"
