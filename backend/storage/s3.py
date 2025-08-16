from typing import Optional
import boto3
from botocore.client import Config
from botocore.exceptions import ClientError
from config import settings

def _client():
    # For MinIO, signature v4 + provide endpoint_url
    return boto3.client(
        "s3",
        endpoint_url=settings.s3_endpoint,
        region_name=settings.s3_region,
        aws_access_key_id=settings.s3_access_key,
        aws_secret_access_key=settings.s3_secret_key,
        config=Config(s3={"addressing_style": "path"}),
        use_ssl=settings.s3_secure,
        verify=settings.s3_secure,  # if false, skip TLS verification (dev)
    )

def ensure_bucket():
    s3 = _client()
    try:
        s3.head_bucket(Bucket=settings.s3_bucket)
    except ClientError:
        # create if not exists
        if settings.s3_region:
            s3.create_bucket(
                Bucket=settings.s3_bucket,
                CreateBucketConfiguration={"LocationConstraint": settings.s3_region},
            )
        else:
            s3.create_bucket(Bucket=settings.s3_bucket)

def presign_put(key: str, content_type: Optional[str], expires_seconds: int = 600) -> str:
    s3 = _client()
    params = {"Bucket": settings.s3_bucket, "Key": key}
    if content_type:
        params["ContentType"] = content_type
    return s3.generate_presigned_url(
        "put_object",
        Params=params,
        ExpiresIn=expires_seconds,
    )

def presign_get(key: str, expires_seconds: int = 600) -> str:
    s3 = _client()
    return s3.generate_presigned_url(
        "get_object",
        Params={"Bucket": settings.s3_bucket, "Key": key},
        ExpiresIn=expires_seconds,
    )
