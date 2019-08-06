"""Squrl lambda function."""
from json import dumps, loads
from os import getenv
from urllib.parse import unquote_plus

from squrl import Squrl


class ApiHandler:
    """AWS API Lambda Handler."""

    @staticmethod
    def get_response(response="OK", error=None):
        """Get a proper, formatted response."""
        statusCode = "400" if error else "200"
        body = str(error) if error else dumps(response)

        return {
            "statusCode": statusCode,
            "body": body,
            "headers": {
                "Content-Type": "application/json",
            },
        }

    def __init__(self, squrl=None, registry=None, handler=None):
        """Override init."""
        self.squrl = squrl if squrl else Squrl(getenv("S3_BUCKET"))

        self.registry = registry if registry else {
            "GET": self.squrl.get,
            "POST": self.squrl.create,
            "PUT": self.squrl.create
        }

        if handler:
            self.handler = handler

    def __call__(self, event, context):
        """Override call."""
        return self.handler(event, context)

    def parse_event(self, event):
        """
        Get the method and body from the event.
        Raise an exception if the method isn't supported.
        """
        method = event["httpMethod"]

        if method not in self.registry.keys():
            raise ValueError(f"Unsupported method: {method}")

        body = loads(event["queryStringParameters"]) if method == "GET" \
            else loads(event["body"])

        return method, body

    def handler(self, event, context):
        """
        Handle the lambda function event and return a response with
        a body containing the url and the key, if it exists.

        response body: '{"url": <string>, "key": <string>}'
        """
        method, body = self.parse_event(event)
        url = unquote_plus(body["url"])
        key = self.registry[method](url)

        return self.get_response(response={"url": url, "key": key})
