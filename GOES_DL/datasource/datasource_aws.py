from typing import Any

import boto3  # type: ignore
from botocore.client import UNSIGNED, ClientError, Config  # type: ignore

from ..utils.url import ParseResult, url
from .datasource import Datasource


class DatasourceAWS(Datasource):
    """
    Abstract a AWS S3 datasource object.

    The AWS S3 datasource is responsible for listing the contents of a
    directory in a remote location and for downloading files from that
    location. The base URL of the datasource is the URL of the AWS S3
    bucket.

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

    def __init__(self, base_url: str) -> None:
        """
        Initialize the AWS S3 datasource.

        Parameters
        ----------
        base_url : str
            The base URL of the AWS S3 bucket.

        Raises
        ------
        ValueError
            If the bucket does not exist or the user has no access.
        """
        url_parts: ParseResult = url.parse(base_url)

        bucket_name: str = url_parts.netloc
        base_path: str = url_parts.path

        self.s3_client: Any = self.get_client()

        if not self.bucket_exists(bucket_name):
            raise ValueError(
                f"Bucket '{bucket_name}' does not exist "
                "or you have no access."
            )

        super().__init__(base_url)

        self.bucket_name: str = bucket_name
        self.base_path: str = base_path

        self.cached: dict[str, list[str]] = {}

    def bucket_exists(self, bucket_name: str) -> bool:
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

    def clear_cache(self, dir_path: str = "") -> None:
        """
        Clear the cache.

        Clear the file list cache of the datasource object.

        Parameters
        ----------
        dir_path : str
            The path to the directory. The path is relative to
            the base URL. If no path is provided, the entire
            cache should be cleared.

        Raises
        ------
        ValueError
            If the folder is not found in the cache.
        """
        if dir_path:
            folder_path: str = self.get_folder_path(dir_path)
            if folder_path in self.cached:
                self.cached.pop(folder_path, None)
                return
            raise ValueError(f"Folder '{dir_path}' not found in cache.")
        else:
            self.cached.clear()

    def get_client(self) -> Any:
        return boto3.client(  # type: ignore
            "s3",
            # region_name="eu-west-1",
            # region_name="us-west-1",
            # region_name="us-east-1",
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
        folder_path: str = self.get_folder_path(file_path)

        try:
            response = self.s3_client.get_object(
                Bucket=self.bucket_name, Key=folder_path
            )
            return response["Body"].read()
        except ClientError as exc:
            message: str = f"Unable to retrieve the file '{file_path}': {exc}"
            raise RuntimeError(message) from exc

    def get_folder_path(self, dir_path: str) -> str:
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
        folder_url = url.join(self.base_url, dir_path)
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
        folder_path: str = self.get_folder_path(dir_path)

        if folder_path in self.cached:
            return self.cached[folder_path]

        paginator: Any = self.s3_client.get_paginator("list_objects_v2")
        pages: Any = paginator.paginate(
            Bucket=self.bucket_name, Prefix=folder_path
        )

        file_list: list[str] = []

        # Workaround for non-existing folders.
        for page in pages:
            if page["KeyCount"] == 0:
                return file_list
            break

        ss: int = len(folder_path)

        file_list.extend(
            f"{dir_path}{obj['Key'][ss:]}"
            for page in pages
            for obj in page["Contents"]
            if obj["Size"] > 0
        )

        self.cached[folder_path] = file_list

        return file_list

    def object_exists(self, bucket_name: str, object_path: str) -> bool:
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
