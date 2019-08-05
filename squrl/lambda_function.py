"""Squrl lambda function."""
import datetime
import hashlib
import json
import os
import urllib

import boto3
import botocore.exceptions


class Squrl:
    """Squrl makes URL's shorter."""
    client = boto3.client("s3")
    key_length = 7
    key_retention = 7

    @classmethod
    def get_key(cls, url):
        """Get a short key for the url prefixed with 'u/'."""
        digest = hashlib.md5(url.encode()).hexdigest()
        return f"u/{digest[:cls.key_length]}"

    @classmethod
    def get_expiration(cls):
        """Get a key expiration datetime object."""
        retention = datetime.timedelta(days=cls.key_retention)
        return datetime.datetime.now() + retention

    def __init__(self, bucket, client=None):
        """Override init."""
        self.bucket = bucket

        if client:
            self.client = client

    def key_exists(self, key):
        """Return True if the specified key exists."""
        try:
            self.client.head_object(Bucket=self.bucket, Key=key)
        except botocore.exceptions.ClientError as e:
            if e.response["Error"]["Code"] == "404":
                return False
            else:
                raise e

        return True

    def get(self, url, **kwargs):
        """Return a key if one exists."""
        key = self.get_key(url)

        return key if self.key_exists(key) else ""

    def create(self, url, **kwargs):
        """Create the short key object with an expiration and redirect."""
        key = self.get_key(url)

        self.client.put_object(
            Bucket=self.bucket,
            Key=key,
            WebsiteRedirectLocation=url,
            Expires=self.get_expiration(),
            ContentType="text/plain"
        )

        return key

    @staticmethod
    def get_response(response="OK", error=None):
        """Get a proper, formatted response."""
        statusCode = "400" if error else "200"
        body = str(error) if error else json.dumps(response)

        return {
            "statusCode": statusCode,
            "body": body,
            "headers": {
                "Content-Type": "application/json",
            },
        }


def handler(event, context):
    """
    Handle the lambda function event and return a response with
    a body containing the url and the key, if it exists.

    response body: '{"url": <string>, "key": <string>}'
    """
    squrl = Squrl(os.getenv("S3_BUCKET"))
    method = event["httpMethod"]
    registry = {
        "GET": squrl.get,
        "POST": squrl.create,
        "PUT": squrl.create
    }

    if method not in registry.keys():
        error = ValueError(f"Unsupported method: {method}")

        return squrl.get_response(error=error)

    body = event["queryStringParameters"] if method == "GET" \
        else json.loads(event["body"])

    url = urllib.parse.unquote_plus(body["url"])
    key = registry[method](url)

    return squrl.get_response(response={"url": url, "key": key})
