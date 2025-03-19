import os

import boto3

AWS_ACCESS_KEY_ID = os.environ["AWS_ACCESS_KEY_ID"]
AWS_SECRET_ACCESS_KEY = os.environ["AWS_SECRET_ACCESS_KEY"]

# Initialize the S3 client
s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name="us-east-2",
)

# Define the bucket name and the file details
bucket_name = "rpi-zero2w-toolhead-camera"
local_file_path = "src/ac_training_lab/A1-cam/_scripts/example_file.txt"
s3_object_name = "example_file.txt"  # This can include subdirectories in S3

# Will be very slow on the NOKIA (UoT preferred)
print(f"Uploading file '{local_file_path}' to '{bucket_name}/{s3_object_name}'...")
s3_client.upload_file(local_file_path, bucket_name, s3_object_name)

print(
    f"File '{local_file_path}' uploaded to '{bucket_name}/{s3_object_name}' successfully."  # noqa: E501
)
