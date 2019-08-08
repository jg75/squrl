"""Lambda Function Handler."""
from os import getenv
from urllib.parse import unquote_plus

from squrl import ApiHandler, Squrl


def handler(event, context, **kwargs):
    """
    Handler.

    Handle the lambda function event and return a response with
    a body containing the url and the key, if it exists.

    response body: '{"url": <string>, "key": <string>}'
    """
    squrlifier = kwargs.get("squrl", Squrl(getenv("S3_BUCKET")))
    registry = kwargs.get(
        "registry",
        {"GET": squrlifier.get, "POST": squrlifier.create, "PUT": squrlifier.create},
    )
    method, body = ApiHandler.parse_event(event)

    if method not in registry.keys():
        error = ValueError(f"Unsupported method: {method}")

        return ApiHandler.get_response(error=error)

    else:
        url = unquote_plus(body["url"])
        key = registry[method](url)

        return ApiHandler.get_response(response={"url": url, "key": key})
