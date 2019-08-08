"""Squrl makes URL's shorter."""
from datetime import datetime, timedelta
from hashlib import md5

import boto3
import botocore.exceptions


class Squrl:
    """
    Squrl makes URL's shorter.

    New keys have a default length of 7 characters and
    a retention period of 7 days
    """

    key_length = 7
    key_retention = 7

    @classmethod
    def get_key(cls, url):
        """Get a short key for the url prefixed with 'u/'."""
        digest = md5(url.encode()).hexdigest()
        return f"u/{digest[:cls.key_length]}"

    @classmethod
    def get_expiration(cls):
        """Get a key expiration datetime object."""
        retention = timedelta(days=cls.key_retention)
        return datetime.now() + retention

    def __init__(self, bucket, client=None):
        """Override init."""
        self.bucket = bucket
        self.client = client if client else boto3.client("s3")

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
            ContentType="text/plain",
        )

        return key
