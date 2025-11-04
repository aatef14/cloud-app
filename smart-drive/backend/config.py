import os


AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
S3_BUCKET_NAME = os.environ.get("S3_BUCKET_NAME", "smart-drive-files")

# DynamoDB tables
DDB_FILES_TABLE = os.environ.get("DDB_FILES_TABLE", "SmartDriveFiles")
DDB_USERS_TABLE = os.environ.get("DDB_USERS_TABLE", "SmartDriveUsers")

JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "change-me-in-prod")


