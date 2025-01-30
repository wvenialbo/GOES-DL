"""
Provide the DatasourceAWS class for handling AWS-based data sources.

Classes:
    DatasourceAWS: Handle AWS-based data sources.
"""

from typing import Literal
from urllib.parse import ParseResult

import boto3
from botocore import UNSIGNED
from botocore.client import ClientError, Config
from mypy_boto3_s3.client import S3Client

from ..dataset import ProductLocator
from ..utils.url import URL
from .datasource_base import DatasourceBase
from .datasource_cache import DatasourceCache

AWS_CLIENT: Literal["s3"] = "s3"


class DatasourceAWS(DatasourceBase):
    """
    Handle AWS-based data sources.

    The AWS S3 datasource is responsible for listing the contents of a
    directory in a remote location and for downloading files from that
    location. The base URL of the datasource is the URL of the AWS S3
    bucket.

    Methods
    -------
    download_file(file_path: str)
        Retrieve a file from the datasource and save it into the local
        repository.
    list_files(dir_path: str)
        List the contents of a remote directory.

    Attributes
    ----------
    bucket_name : str
        The name of the AWS S3 bucket.
    s3_client : S3Client
        The AWS S3 client.
    """

    bucket_name: str
    s3_client: S3Client

    def __init__(
        self,
        locator: ProductLocator | tuple[str, ...],
        cache: float | DatasourceCache | None = None,
    ) -> None:
        """
        Initialize the DatasourceAWS object.

        Parameters
        ----------
        locator : ProductLocator | tuple[str, ...]
            A `ProductLocator` object or a tuple of strings containing
            the base URL and an optional region where the S3 bucket is
            located. E.g. "us-west-1", "us-east-1", "eu-west-1", etc. If
            None, the default region is used.
        cache : float | DatasourceCache | None, optional
            The cache expiration time in seconds, by default None.

        Raises
        ------
        ValueError
            If the bucket does not exist or the user has no access.
        """
        base_url: str
        region: str | None
        if isinstance(locator, ProductLocator):
            (base_url, region) = locator.get_base_url("AWS")
        else:
            (base_url, region) = locator

        url_parts: ParseResult = URL.parse(base_url)

        bucket_name: str = url_parts.netloc

        self.s3_client: S3Client = self._get_client(region)

        if not self._bucket_exists(bucket_name):
            raise ValueError(
                f"Bucket '{bucket_name}' does not exist or you have no access."
            )

        super().__init__(base_url, cache)

        self.bucket_name: str = bucket_name

    def download_file(self, file_path: str) -> bytes:
        """
        Download a file from the datasource into the local repository.

        Get a file from a remote location or local repository. The path
        provided must be relative to the base URL and local repository
        root directory. The remote path is reconstructed in the local
        repository.

        Parameters
        ----------
        file_path : str
            The path to the remote file to be downloaded.

        Returns
        -------
        bytes
            The content of the file as a byte string.

        Raises
        ------
        RuntimeError
            If the file cannot be retrieved.
        """
        try:
            return self._retrieve_file(file_path)

        except ClientError as exc:
            raise RuntimeError(
                f"Unable to retrieve the file '{file_path}': {exc}"
            ) from exc

    def list_files(self, dir_path: str) -> list[str]:
        """
        List the contents of a directory.

        List the contents of a directory in a remote location. The path
        is relative to the base URL.

        Parameters
        ----------
        dir_path : str
            The path to the directory. The path is relative to the base
            URL.

        Returns
        -------
        list[str]
            A list of file names in the directory.
        """
        cached_list = self.cache.get_item(dir_path)

        if cached_list is not None:
            return cached_list

        folder_path = self._get_item_path(dir_path)

        paginator = self.s3_client.get_paginator("list_objects_v2")
        pages = paginator.paginate(Bucket=self.bucket_name, Prefix=folder_path)

        # Workaround for non-existing folders.
        for page in pages:
            if page["KeyCount"] == 0:
                return []

            break

        ss = len(folder_path)

        file_list: list[str] = []

        file_list.extend(
            f"{dir_path}{obj['Key'][ss:]}"
            for page in pages
            for obj in page["Contents"]
            if obj["Size"] > 0
        )

        self.cache.add_item(dir_path, file_list)

        return file_list

    def _bucket_exists(self, bucket_name: str) -> bool:
        try:
            self.s3_client.head_bucket(Bucket=bucket_name)

        except ClientError:  # as exc
            # Bucket not found error or host is out of service (log this!)
            return False

        return True

    @staticmethod
    def _get_client(region: str | None) -> S3Client:
        if region:
            return boto3.client(
                AWS_CLIENT,
                region_name=region,
                config=Config(signature_version=UNSIGNED),
            )

        return boto3.client(
            AWS_CLIENT,
            config=Config(signature_version=UNSIGNED),
        )

    def _get_item_path(self, dir_path: str) -> str:

        folder_url = self._url_join(self.base_url, dir_path)

        url_parts = URL.parse(folder_url)

        return url_parts.path[1:]

    def _object_exists(self, bucket_name: str, object_path: str) -> bool:
        try:
            self.s3_client.head_object(Bucket=bucket_name, Key=object_path)

        except ClientError:  # as exc
            # Object not found error or host is out of service (log this!)
            return False

        return True

    def _retrieve_file(self, file_path: str) -> bytes:
        folder_path = self._get_item_path(file_path)

        response = self.s3_client.get_object(
            Bucket=self.bucket_name, Key=folder_path
        )

        return response["Body"].read()

    @staticmethod
    def _url_join(head: str, tail: str) -> str:
        # Note: url.join() fails with "s3://" URLs.
        # > folder_url: str = url.join(self.base_url, dir_path)

        if head.endswith("/") and tail.startswith("/"):
            head = head[:-1]

        if not head.endswith("/") and not tail.startswith("/"):
            return f"{head}/{tail}"

        return head + tail
