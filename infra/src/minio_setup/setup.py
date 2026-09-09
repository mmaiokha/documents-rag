from minio import Minio
from minio.commonconfig import Filter
from minio.lifecycleconfig import Expiration, LifecycleConfig, Rule
from config.settings import settings


MINIO_ENDPOINT = settings.minio_url
MINIO_ACCESS_KEY = settings.minio_user
MINIO_SECRET_KEY = settings.minio_password
MINIO_SECURE = settings.minio_secure


DOCUMENTS_BUCKET = 'documents'


def create_client() -> Minio:
    return Minio(
        endpoint=MINIO_ENDPOINT,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=MINIO_SECURE,
    )


def ensure_bucket(client: Minio, bucket: str) -> None:
    if not client.bucket_exists(bucket):
        client.make_bucket(bucket)
        print(f"Created bucket: {bucket}")
    else:
        print(f"Bucket already exists: {bucket}")


def configure_lifecycle(client: Minio) -> None:
    tmp_config = LifecycleConfig(
        [
            Rule(
                rule_id="expire-temp-uploads",
                status="Enabled",
                rule_filter=Filter(prefix="tmp/"),
                expiration=Expiration(days=1),
            )
        ]
    )

    client.set_bucket_lifecycle(
        DOCUMENTS_BUCKET,
        tmp_config,
    )

    print("Lifecycle configured")


def setup_minio() -> None:
    client = create_client()

    ensure_bucket(client, DOCUMENTS_BUCKET)
    configure_lifecycle(client)