from os import getenv
from urllib.parse import unquote_plus

from squrl import ApiHandler, Squrl


def handler(event, context, squrl=None, registry=None):
    """
    Handle the lambda function event and return a response with
    a body containing the url and the key, if it exists.

    response body: '{"url": <string>, "key": <string>}'
    """
    squrl = squrl if squrl else Squrl(getenv("S3_BUCKET"))
    registry = registry if registry else {
        "GET": squrl.get,
        "POST": squrl.create,
        "PUT": squrl.create
    }
    method, body = ApiHandler.parse_event(event)

    if method not in registry.keys():
        raise ValueError(f"Unsupported method: {method}")

    url = unquote_plus(body["url"])
    key = registry[method](url)

    return ApiHandler.get_response(response={"url": url, "key": key})
