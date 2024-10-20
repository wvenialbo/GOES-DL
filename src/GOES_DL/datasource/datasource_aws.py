"""
Provide the DatasourceAWS class for handling AWS-based data sources.

Classes:
    DatasourceAWS: Handle AWS-based data sources.
"""

from typing import Any, overload
from urllib.parse import ParseResult

import boto3
from botocore import UNSIGNED
from botocore.client import ClientError, Config

from ..dataset import ProductLocator
from ..utils.url import url
from .datasource import Datasource
from .datasource_cache import DatasourceCache

AWS_CLIENT: str = "s3"


class DatasourceAWS(Datasource):
    """
    Handle AWS-based data sources.

    The AWS S3 datasource is responsible for listing the contents of a
    directory in a remote location and for downloading files from that
    location. The base URL of the datasource is the URL of the AWS S3
    bucket.

    Parameters
    ----------
    locator : tuple[str, ...] | ProductLocator
        A `ProductLocator` object or a tuple of strings containing
        the base URL and an optional region where the S3 bucket is
        located. E.g. "us-west-1", "us-east-1", "eu-west-1", etc. If
        None, the default region is used.

    Attributes
    ----------
    base_url : str
        The base URL of the datasource. This is the URL where the
        datasource is located. The base URL is used to build the full
        URL to the files and directories.
    bucket_name : str
        The name of the AWS S3 bucket.
    base_path : str
        The base path of the AWS S3 bucket.
    s3_client : boto3.Client
        The AWS S3 client.
    cached : dict[str, list[str]]
        The cached file lists in the datasource, organised by folder.

    Methods
    -------
    bucket_exists(bucket_name: str) -> bool
        Check if the bucket exists.
    clear_cache(dir_path: str = "") -> None
        Clear the cache.
    get_client() -> Any
        Get the AWS S3 client.
    get_file(file_path: str) -> Any
        Download a file into memory.
    get_folder_path(dir_path: str) -> str
        Get the folder path.
    listdir(dir_path: str) -> list[str]
        List the contents of a directory.
    object_exists(bucket_name: str, object_path: str) -> bool
        Check if the object exists.

    Raises
    ------
    ValueError
        If the bucket does not exist or the user has no access.
    """

    @overload
    def __init__(
        self, locator: tuple[str, ...], cache: DatasourceCache | None = None
    ) -> None: ...

    @overload
    def __init__(
        self, locator: ProductLocator, cache: DatasourceCache | None = None
    ) -> None: ...

    def __init__(
        self,
        locator: ProductLocator | tuple[str, ...],
        cache: DatasourceCache | None = None,
    ) -> None:
        base_url: str
        region: str | None
        if isinstance(locator, ProductLocator):
            (base_url, region) = locator.get_base_url("AWS")
        else:
            (base_url, region) = locator

        url_parts: ParseResult = url.parse(base_url)

        bucket_name: str = url_parts.netloc

        self.s3_client: Any = self._get_client(region)

        if not self._bucket_exists(bucket_name):
            raise ValueError(
                f"Bucket '{bucket_name}' does not exist or you have no access."
            )

        super().__init__(base_url)

        self.bucket_name: str = bucket_name

        self.cache: DatasourceCache = cache or DatasourceCache()

    @overload
    @staticmethod
    def create(
        locator: ProductLocator, life_time: float | None = None
    ) -> "DatasourceAWS": ...

    @overload
    @staticmethod
    def create(
        locator: tuple[str, ...], life_time: float | None = None
    ) -> "DatasourceAWS": ...

    @staticmethod
    def create(
        locator: tuple[str, ...] | ProductLocator,
        life_time: float | None = None,
    ) -> "DatasourceAWS":
        """
        Create a new AWS-based datasource.

        Create a new AWS-based datasource with a base URL or a
        ProductLocator object.

        Parameters
        ----------
        locator : str
            The base URL of a HTTP folder or a `ProductLocator` object.
        life_time : float, optional
            The cache life time in seconds, by default None.

        Returns
        -------
        DatasourceHTTP
            A new `DatasourceHTTP` object.

        Raises
        ------
        ValueError
            If the resource does not exist or the user has no access.
        """
        cache = DatasourceCache(life_time)
        return DatasourceAWS(locator, cache)

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

    def _get_client(self, region: str | None) -> Any:
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
        Any
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

    def get_file(self, file_path: str) -> Any:
        """
        Download a file into memory.

        Get a file from a remote location. The path is relative to the
        base URL.

        Parameters
        ----------
        file_path : str
            The path to the file. The path is relative to the base URL.

        Returns
        -------
        Any
            The file object.

        Raises
        ------
        RuntimeError
            If the file cannot be retrieved.
        """
        folder_path: str = self.get_item_path(file_path)

        try:
            response: Any = self.s3_client.get_object(
                Bucket=self.bucket_name, Key=folder_path
            )
            return response["Body"].read()

        except ClientError as exc:
            message: str = f"Unable to retrieve the file '{file_path}': {exc}"
            raise RuntimeError(message) from exc

    @staticmethod
    def _url_join(head: str, tail: str) -> str:
        if head.endswith("/") and tail.startswith("/"):
            head = head[:-1]
        if not head.endswith("/") and not tail.startswith("/"):
            return head + "/" + tail
        return head + tail

    def get_item_path(self, dir_path: str) -> str:
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

        folder_path: str = self.get_item_path(dir_path)

        paginator: Any = self.s3_client.get_paginator("list_objects_v2")
        pages: Any = paginator.paginate(
            Bucket=self.bucket_name, Prefix=folder_path
        )

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
