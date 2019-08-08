"""Squrl lambda function."""
from json import dumps, loads


class ApiHandler:
    """AWS API Lambda Handler."""

    @staticmethod
    def parse_event(event):
        """
        Get the method and body from the event.

        Raise an exception if the method isn't supported.
        """
        method = event["httpMethod"]

        body = (
            loads(event["queryStringParameters"])
            if method == "GET"
            else loads(event["body"])
        )

        return method, body

    @staticmethod
    def get_response(response="OK", error=None):
        """Get a proper, formatted response."""
        statusCode = "400" if error else "200"
        body = str(error) if error else dumps(response)

        return {
            "statusCode": statusCode,
            "body": body,
            "headers": {"Content-Type": "application/json"},
        }

    def __init__(self, handler):
        """Override init."""
        self.handler = handler

    def __call__(self, event, context, **kwargs):
        """Override call."""
        return self.handler(event, context, **kwargs)
