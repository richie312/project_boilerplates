import boto3
from boto3 import client


class AWS:
    def __init__(self):
        self.s3 = boto3.resource("s3")
        self.conn = client("s3")

    def s3_read_file(self, bucket_name, file_name):
        csv_obj = self.conn.get_object(Bucket=bucket_name, Key=file_name)
        data = csv_obj.get("Body")
        return data

    def s3_list_files(self, bucket_name):
        file_list = [
            key["Key"] for key in self.conn.list_objects(Bucket=bucket_name)["Contents"]
        ]
        return file_list
