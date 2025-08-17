from typing import Optional, List
import boto3
from botocore.client import Config
from botocore.exceptions import ClientError
from config import settings

def put_bucket_cors(origins: List[str]):
    s3 = _client()
    cors = {
        "CORSRules": [
            {
                "AllowedMethods": ["PUT", "GET"],
                "AllowedOrigins": origins,
                "AllowedHeaders": ["*"],
                "ExposeHeaders": ["ETag"],
                "MaxAgeSeconds": 3600,
            }
        ]
    }
    s3.put_bucket_cors(Bucket=settings.s3_bucket, CORSConfiguration=cors)

# backend/storage/s3.py
from typing import Optional, List
import boto3
from botocore.client import Config
from botocore.exceptions import ClientError
from config import settings

def _client():
    return boto3.client(
        "s3",
        endpoint_url=settings.s3_endpoint,
        region_name=settings.s3_region or "us-east-1",
        aws_access_key_id=settings.s3_access_key,
        aws_secret_access_key=settings.s3_secret_key,
        config=Config(s3={"addressing_style": "path"}, signature_version="s3v4"),
        use_ssl=settings.s3_secure,
        verify=settings.s3_secure,
    )

def head_object(key: str) -> dict:
    s3 = _client()
    return s3.head_object(Bucket=settings.s3_bucket, Key=key)


def ensure_bucket():
    s3 = _client()
    try:
        s3.head_bucket(Bucket=settings.s3_bucket)
    except ClientError:
        if settings.s3_region:
            s3.create_bucket(
                Bucket=settings.s3_bucket,
                CreateBucketConfiguration={"LocationConstraint": settings.s3_region},
            )
        else:
            s3.create_bucket(Bucket=settings.s3_bucket)

def put_bucket_cors(origins: List[str]):
    s3 = _client()
    cors = {
        "CORSRules": [
            {
                "AllowedMethods": ["PUT", "GET"],
                "AllowedOrigins": origins,
                "AllowedHeaders": ["*"],
                # Some gateways choke on ExposeHeaders/MaxAge; start minimal.
                "MaxAgeSeconds": 3600,
            }
        ]
    }
    try:
        s3.put_bucket_cors(Bucket=settings.s3_bucket, CORSConfiguration=cors)
    except ClientError as e:
        code = (e.response or {}).get("Error", {}).get("Code")
        if code in {"NotImplemented", "XNotImplemented"}:
            # Older MinIO / gateway mode: CORS API not available. Warn and continue.
            print(f"WARNING: PutBucketCors not supported by endpoint; set bucket CORS manually for '{settings.s3_bucket}'.")
        else:
            raise

def ensure_bucket_with_cors():
    ensure_bucket()
    try:
        put_bucket_cors([settings.frontend_origin])
    except ClientError:
        # As a last resort, never block presign on CORS setup.
        pass

def presign_put(key: str, content_type: Optional[str], expires_seconds: int = 600) -> str:
    s3 = _client()
    params = {"Bucket": settings.s3_bucket, "Key": key}
    if content_type:
        params["ContentType"] = content_type
    return s3.generate_presigned_url("put_object", Params=params, ExpiresIn=expires_seconds)

def presign_get(key: str, expires_seconds: int = 600) -> str:
    s3 = _client()
    return s3.generate_presigned_url("get_object", Params={"Bucket": settings.s3_bucket, "Key": key}, ExpiresIn=expires_seconds)
