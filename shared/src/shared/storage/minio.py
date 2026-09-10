from minio import Minio
from minio.commonconfig import CopySource
from datetime import timedelta

class ObjectStorage:
    def __init__(self, endpoint, access_key, secret_key, secure = True):
    
        self.client = Minio(
            endpoint=endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=secure
        )


    def get_presigned_url(
        self, bucket, object_name, expires: timedelta = timedelta(minutes=15)
    ) -> str:
        return self.client.presigned_put_object(bucket, object_name, expires)

    def file_exists(self, bucket: str, object_name: str) -> bool:
        try:
            self.client.stat_object(bucket, object_name)
            return True
        except Exception:
            return False

    def make_permanent(
        self,
        bucket: str,
        source: str,
        destination: str,
    ) -> None:
        self.client.copy_object(
            bucket,
            destination,
            CopySource(bucket, source),
        )

        self.client.remove_object(bucket, source)
        
    def get_presigned_get_url(
        self,
        bucket: str,
        object_name: str,
        expires: timedelta = timedelta(minutes=15),
    ) -> str:
        return self.client.presigned_get_object(
            bucket,
            object_name,
            expires=expires,
        )
