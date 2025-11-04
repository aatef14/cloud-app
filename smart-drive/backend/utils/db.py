from typing import Any, Dict, List, Optional, Tuple


def get_tables(ddb_resource, users_table_name: str, files_table_name: str):
    users_table = ddb_resource.Table(users_table_name)
    files_table = ddb_resource.Table(files_table_name)
    return users_table, files_table


# Users
def create_user(users_table, username: str, password_hash: str) -> None:
    users_table.put_item(
        Item={
            "username": username,
            "password_hash": password_hash,
        },
        ConditionExpression="attribute_not_exists(username)",
    )


def get_user_by_username(users_table, username: str) -> Optional[Dict[str, Any]]:
    resp = users_table.get_item(Key={"username": username})
    return resp.get("Item")


# Files
def put_file_item(
    files_table,
    username: str,
    file_name: str,
    file_url: str,
    s3_key: str,
    upload_date: str,
) -> None:
    files_table.put_item(
        Item={
            "username": username,
            "file_name": file_name,
            "file_url": file_url,
            "s3_key": s3_key,
            "upload_date": upload_date,
        }
    )


def list_files_for_user(files_table, username: str) -> List[Dict[str, Any]]:
    # Assumes a table with partition key: username, sort key: file_name
    resp = files_table.query(
        KeyConditionExpression="#u = :u",
        ExpressionAttributeNames={"#u": "username"},
        ExpressionAttributeValues={":u": username},
    )
    items = resp.get("Items", [])
    items_sorted = sorted(items, key=lambda x: x.get("file_name", "").lower())
    return items_sorted


def delete_file_item(files_table, username: str, file_name: str) -> None:
    files_table.delete_item(Key={"username": username, "file_name": file_name})


