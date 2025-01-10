"""
Provide the DatasourceAWS class for handling AWS-based data sources.

Classes:
    DatasourceAWS: Handle AWS-based data sources.
"""

from pathlib import Path
from typing import Literal
from urllib.parse import ParseResult

import boto3
from botocore import UNSIGNED
from botocore.client import ClientError, Config
from mypy_boto3_s3.client import S3Client

from ..dataset import ProductLocator
from ..utils.url import URL as url
from .constants import DownloadStatus
from .datasource_base import DatasourceBase
from .datasource_cache import DatasourceCache
from .datasource_repository import DatasourceRepository

AWS_CLIENT: Literal["s3"] = "s3"


class DatasourceAWS(DatasourceBase):
    """
    Handle AWS-based data sources.

    The AWS S3 datasource is responsible for listing the contents of a
    directory in a remote location and for downloading files from that
    location. The base URL of the datasource is the URL of the AWS S3
    bucket.

    Attributes
    ----------
    bucket_name : str
        The name of the AWS S3 bucket.
    s3_client : boto3.Client
        The AWS S3 client.

    Methods
    -------
    download_file(file_path: str)
        Retrieve a file from the datasource and save it into the local
        repository.
    listdir(dir_path: str)
        List the contents of a remote directory.
    """

    bucket_name: str
    s3_client: S3Client

    def __init__(
        self,
        locator: ProductLocator | tuple[str, ...],
        repository: str | Path | DatasourceRepository | None = None,
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
        repository : str | Path | DatasourceRepository, optional
            The directory where the files will be stored, by default
            None.
        cache : float | DatasourceCache, optional
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

        url_parts: ParseResult = url.parse(base_url)

        bucket_name: str = url_parts.netloc

        self.s3_client: S3Client = self._get_client(region)

        if not self._bucket_exists(bucket_name):
            raise ValueError(
                f"Bucket '{bucket_name}' does not exist or you have no access."
            )

        super().__init__(base_url, repository, cache)

        self.bucket_name: str = bucket_name

    def download_file(self, file_path: str) -> DownloadStatus:
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
        DownloadStatus
            `DownloadStatus.SUCCESS` if the file was downloaded
            successfully; otherwise, `DownloadStatus.ALREADY` if the
            file is already in the local repository.

        Raises
        ------
        RuntimeError
            If the file cannot be retrieved.
        """
        if self.repository.has_item(file_path):
            return DownloadStatus.ALREADY

        try:
            self._retrieve_file(file_path)
            return DownloadStatus.SUCCESS

        except ClientError as exc:
            message: str = f"Unable to retrieve the file '{file_path}': {exc}"
            raise RuntimeError(message) from exc

    def listdir(self, dir_path: str) -> list[str]:
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

        folder_path: str = self._get_item_path(dir_path)

        paginator = self.s3_client.get_paginator("list_objects_v2")
        pages = paginator.paginate(Bucket=self.bucket_name, Prefix=folder_path)

        # Workaround for non-existing folders.
        for page in pages:
            if page["KeyCount"] == 0:
                return []

            break

        ss: int = len(folder_path)

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
        """
        Check if the bucket exists.

        Check if the bucket exists in the AWS S3 service.

        Parameters
        ----------
        bucket_name : str
            The name of the bucket to check.

        Returns
        -------
        bool
            True if the bucket exists, False otherwise.
        """
        try:
            self.s3_client.head_bucket(Bucket=bucket_name)

        except ClientError as exc:
            print(exc)
            return False

        return True

    @staticmethod
    def _get_client(region: str | None) -> S3Client:
        """
        Get the AWS S3 client.

        Returns the AWS S3 client with the UNSIGNED signature version.

        Parameters
        ----------
        region : str
            The region where the S3 bucket is located. E.g. "us-west-1",
            "us-east-1", "eu-west-1", etc. If None, the default region
            is used.

        Returns
        -------
        S3Client
            The AWS S3 client.
        """
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
        """
        Get the folder path.

        Get the folder path from the base URL and the directory path.

        Parameters
        ----------
        dir_path : str
            The path to the directory. The path is relative to the base
            URL.

        Returns
        -------
        str
            The folder path.
        """
        # BUG: url.join() fails with "s3://" URLs.
        # > folder_url: str = url.join(self.base_url, dir_path)
        folder_url: str = self._url_join(self.base_url, dir_path)
        url_parts: ParseResult = url.parse(folder_url)

        return url_parts.path[1:]

    def _object_exists(self, bucket_name: str, object_path: str) -> bool:
        """
        Check if the object exists.

        Check if the object exists in the AWS S3 service.

        Parameters
        ----------
        bucket_name : str
            The name of the bucket where the object is located.
        object_path : str
            The path to the object to check.

        Returns
        -------
        bool
            True if the object exists, False otherwise.
        """
        try:
            self.s3_client.head_object(Bucket=bucket_name, Key=object_path)

        except ClientError as exc:
            print(exc)

            return False

        return True

    def _retrieve_file(self, file_path: str) -> bytes:
        folder_path: str = self._get_item_path(file_path)

        response = self.s3_client.get_object(
            Bucket=self.bucket_name, Key=folder_path
        )
        content = response["Body"].read()
        self.repository.add_item(file_path, content)

        return content

    @staticmethod
    def _url_join(head: str, tail: str) -> str:
        if head.endswith("/") and tail.startswith("/"):
            head = head[:-1]
        if not head.endswith("/") and not tail.startswith("/"):
            return f"{head}/{tail}"
        return head + tail
