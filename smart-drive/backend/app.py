from datetime import datetime, timedelta
import os

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
import boto3
from botocore.exceptions import ClientError

from config import (
    AWS_REGION,
    S3_BUCKET_NAME,
    DDB_FILES_TABLE,
    DDB_USERS_TABLE,
    JWT_SECRET_KEY,
)
from utils.db import (
    get_tables,
    create_user,
    get_user_by_username,
    put_file_item,
    list_files_for_user,
    delete_file_item,
)


def create_app() -> Flask:
    app = Flask(__name__)
    CORS(app)
    app.config["JWT_SECRET_KEY"] = JWT_SECRET_KEY
    jwt = JWTManager(app)

    # AWS clients/resources
    s3_client = boto3.client("s3", region_name=AWS_REGION)
    ddb = boto3.resource("dynamodb", region_name=AWS_REGION)
    users_table, files_table = get_tables(ddb, DDB_USERS_TABLE, DDB_FILES_TABLE)

    @app.get("/")
    def health():
        return jsonify({"status": "ok", "service": "Cloud-smart-storage"})

    # Auth
    @app.post("/register")
    def register():
        data = request.get_json(force=True)
        username = (data or {}).get("username", "").strip()
        password = (data or {}).get("password", "")

        if not username or not password:
            return jsonify({"message": "username and password are required"}), 400

        existing = get_user_by_username(users_table, username)
        if existing:
            return jsonify({"message": "user already exists"}), 409

        password_hash = generate_password_hash(password)
        create_user(users_table, username, password_hash)
        return jsonify({"message": "registered"}), 201

    @app.post("/login")
    def login():
        data = request.get_json(force=True)
        username = (data or {}).get("username", "").strip()
        password = (data or {}).get("password", "")

        if not username or not password:
            return jsonify({"message": "username and password are required"}), 400

        user = get_user_by_username(users_table, username)
        if not user or not check_password_hash(user.get("password_hash", ""), password):
            return jsonify({"message": "invalid credentials"}), 401

        access_token = create_access_token(identity=username, expires_delta=timedelta(hours=12))
        return jsonify({"access_token": access_token})

    # Files
    @app.post("/upload")
    @jwt_required()
    def upload_file():
        username = get_jwt_identity()
        if "file" not in request.files:
            return jsonify({"message": "no file part"}), 400

        file = request.files["file"]
        if file.filename == "":
            return jsonify({"message": "no selected file"}), 400

        object_key = f"{username}/{file.filename}"
        try:
            s3_client.upload_fileobj(
                Fileobj=file,
                Bucket=S3_BUCKET_NAME,
                Key=object_key,
                ExtraArgs={"ContentType": file.mimetype or "application/octet-stream"},
            )
        except ClientError as e:
            return jsonify({"message": "upload failed", "error": str(e)}), 500

        file_url = f"https://{S3_BUCKET_NAME}.s3.amazonaws.com/{object_key}"
        now_str = datetime.utcnow().strftime("%Y-%m-%d")
        put_file_item(files_table, username, file.filename, file_url, object_key, now_str)
        return jsonify({"message": "uploaded", "file_url": file_url})

    @app.get("/files")
    @jwt_required()
    def list_files():
        username = get_jwt_identity()
        items = list_files_for_user(files_table, username)
        return jsonify({"files": items})

    @app.delete("/delete/<path:filename>")
    @jwt_required()
    def delete_file(filename: str):
        username = get_jwt_identity()
        object_key = f"{username}/{filename}"
        try:
            s3_client.delete_object(Bucket=S3_BUCKET_NAME, Key=object_key)
        except ClientError as e:
            return jsonify({"message": "delete failed", "error": str(e)}), 500

        delete_file_item(files_table, username, filename)
        return jsonify({"message": "deleted"})

    @app.get("/share/<path:filename>")
    @jwt_required()
    def share_file(filename: str):
        username = get_jwt_identity()
        object_key = f"{username}/{filename}"
        try:
            url = s3_client.generate_presigned_url(
                ClientMethod="get_object",
                Params={"Bucket": S3_BUCKET_NAME, "Key": object_key},
                ExpiresIn=3600,
            )
        except ClientError as e:
            return jsonify({"message": "could not generate link", "error": str(e)}), 500

        return jsonify({"share_url": url, "expires_in": 3600})

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)


