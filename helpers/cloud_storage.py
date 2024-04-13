import enum
import logging

import boto3
from boto3.exceptions import Boto3Error

from settings import settings

logger = logging.getLogger(__name__)


class CloudMediaStorageAdapter:
    __access_key = settings.S3_CLOUD_KEY
    __secret_key = settings.S3_CLOUD_SECRET
    __bucket_name = settings.BUCKET_NAME
    __price_tags_link = settings.BUCKET_PUBLIC_PATH

    __s3 = boto3.client(
        "s3", endpoint_url="https://s3.storage.selcloud.ru",
        region_name="ru-1",
        aws_access_key_id=__access_key, aws_secret_access_key=__secret_key
    )

    @classmethod
    def upload_new_price_tag(cls, file: bytes, file_name: str):
        try:
            cls.__s3.put_object(
                Bucket=cls.__bucket_name,
                Key=file_name,
                Body=file,
            )
            logger.info(f"Ценник загружен по пути: ****/{file_name}")
            return f"{cls.__price_tags_link}/{file_name}"
        except Boto3Error as e:
            logger.error(e)
