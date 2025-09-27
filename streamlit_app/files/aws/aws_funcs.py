import boto3
import streamlit as st
import os

from botocore.exceptions import NoCredentialsError

try:
    S3_BUCKET_NAME_PROJECTS = os.environ['S3_BUCKET_NAME_PROJECTS']
    AWS_ACCESS_KEY_PROJECTS = os.environ['AWS_ACCESS_KEY_PROJECTS']
    AWS_SECRET_KEY_PROJECTS = os.environ['AWS_SECRET_KEY_PROJECTS']
except Exception as e:
    st.info(e)



def upload_to_s3(file_path: str, object_path_in_s3: str) -> None:
    """Uploads a file to an S3 bucket at the specified path.

    This function transfers a local file to the configured S3 bucket using the provided object path.

    Args:
        file_path (str): The local path to the file to upload.
        object_path_in_s3 (str): The destination path in the S3 bucket.

    Returns:
        None
    """
    s3_client = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_PROJECTS, aws_secret_access_key=AWS_SECRET_KEY_PROJECTS)

    try:
        s3_client.upload_file(file_path, S3_BUCKET_NAME_PROJECTS, object_path_in_s3) 
    except NoCredentialsError:
        print('Credentials not available')


def upload_to_s3_obj(file_obj, object_path_in_s3: str) -> None:
    """Uploads a file-like object to an S3 bucket at the specified path.

    This function transfers a file-like object to the configured S3 bucket using the provided object path.

    Args:
        file_obj: The file-like object to upload.
        object_path_in_s3 (str): The destination path in the S3 bucket.

    Returns:
        int: Returns 0 if the upload fails, otherwise None.
    """
    s3_client = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_PROJECTS, aws_secret_access_key=AWS_SECRET_KEY_PROJECTS)

    try:
        s3_client.upload_fileobj(file_obj, S3_BUCKET_NAME_PROJECTS, object_path_in_s3)
    except Exception as e:
        print(f'Failed to upload file to S3: {e}')
        return 0

def download_from_s3(object_path_in_s3, file_path):
    """Downloads a file from an S3 bucket to a local path.

    This function retrieves a file from the configured S3 bucket and saves it to the specified local file path.

    Args:
        object_path_in_s3 (str): The path of the object in the S3 bucket.
        file_path (str): The local path to save the downloaded file.

    Returns:
        None
    """
    s3_client = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_PROJECTS, aws_secret_access_key=AWS_SECRET_KEY_PROJECTS)

    try:
        file = s3_client.download_file(S3_BUCKET_NAME_PROJECTS, object_path_in_s3, file_path)
        print(f'Object {object_path_in_s3} has been downloaded from {S3_BUCKET_NAME_PROJECTS} to {file_path}')
    except NoCredentialsError:
        print('Credentials not available')
    except Exception as e:
        print(f'An error occurred: {e}')

def get_from_s3(object_path_in_s3):
    """Retrieves an object from an S3 bucket.

    This function fetches the specified object from the configured S3 bucket and returns its contents.

    Args:
        object_path_in_s3 (str): The path of the object in the S3 bucket.

    Returns:
        dict or int: The S3 object dictionary if successful, otherwise 0.
    """
    s3_client = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_PROJECTS, aws_secret_access_key=AWS_SECRET_KEY_PROJECTS)

    try:
        return s3_client.get_object(Bucket=S3_BUCKET_NAME_PROJECTS, Key=object_path_in_s3)
    except NoCredentialsError:
        print('Credentials not available')
    except Exception as e:
        print(f'?An error occurred: {e}')
    return 0 

def delete_folder_from_s3(folder_path):
    s3_client = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_PROJECTS, aws_secret_access_key=AWS_SECRET_KEY_PROJECTS)

    try:
        objects_to_delete = s3_client.list_objects_v2(Bucket=S3_BUCKET_NAME_PROJECTS, Prefix=folder_path)
        
        object_keys = [obj['Key'] for obj in objects_to_delete.get('Contents', [])]
        
        if object_keys:
            response = s3_client.delete_objects(
                Bucket=S3_BUCKET_NAME_PROJECTS,
                Delete={
                    'Objects': [{'Key': obj_key} for obj_key in object_keys]
                }
            )
            print(f'Deleted objects: {object_keys}')
        else:
            print(f'No objects found in folder: {folder_path}')
    except NoCredentialsError:
        print('Credentials not available')
    except Exception as e:
        print(f'!An error occurred: {e}')

def delete_object_from_s3(object_key):
    """Deletes a specific object from an S3 bucket.

    This function removes the object identified by the given key from the configured S3 bucket.

    Args:
        object_key (str): The key (path) of the object to delete in the S3 bucket.

    Returns:
        None
    """
    s3_client = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_PROJECTS, aws_secret_access_key=AWS_SECRET_KEY_PROJECTS)

    try:
        response = s3_client.delete_object(
            Bucket=S3_BUCKET_NAME_PROJECTS,
            Key=object_key
        )
        print(response)
        print(f'Deleted object: {object_key}')
    except NoCredentialsError:
        print('Credentials not available')
    except Exception as e:
        print(f'!!An error occurred: {e}')


def read_s3_file(bucket_name, file_key):
    """Reads the contents of a file from an S3 bucket.

    This function retrieves and decodes the contents of the specified file from the given S3 bucket.

    Args:
        bucket_name (str): The name of the S3 bucket.
        file_key (str): The key (path) of the file in the S3 bucket.

    Returns:
        str: The decoded contents of the file, or an empty string if the file does not exist or an error occurs.
    """
    s3_client = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_PROJECTS, aws_secret_access_key=AWS_SECRET_KEY_PROJECTS)
    try:
        s3_object = s3_client.get_object(Bucket=bucket_name, Key=file_key)
        return s3_object['Body'].read().decode('utf-8')
    except s3_client.exceptions.NoSuchKey:
        return ""
    except Exception as e:
        print(f"Error reading file from S3: {e}")
        return ""

def write_to_s3(bucket_name, file_key, content):
    """Writes content to a file in an S3 bucket.

    This function uploads the provided content as a file to the specified S3 bucket and key.

    Args:
        bucket_name (str): The name of the S3 bucket.
        file_key (str): The key (path) for the file in the S3 bucket.
        content (str): The content to write to the file.

    Returns:
        None
    """
    s3_client = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_PROJECTS, aws_secret_access_key=AWS_SECRET_KEY_PROJECTS)
    try:
        s3_client.put_object(Bucket=bucket_name, Key=file_key, Body=content.encode('utf-8'))
        print(f'File has been uploaded to {bucket_name}/{file_key}')
    except Exception as e:
        print(f"Error writing file to S3: {e}")