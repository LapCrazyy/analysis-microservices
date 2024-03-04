import os
def download_file_by_patterns(minio_client, download_dir, bucket_name, patterns, reset=False):
    try:
        objects_list = minio_client.list_objects(Bucket=bucket_name)
        for obj in objects_list.get('Contents', []):
            object_key = obj['Key']

            if all(pattern not in object_key for pattern in patterns):  #fix for converter
                print(f"Skipping: {object_key} from bucket {bucket_name}")
                continue
            object_path = os.path.join(download_dir, object_key)
            minio_client.download_file(bucket_name, object_key, object_path)
            print(f"Download completed: {object_path} from bucket {bucket_name}")
            if unzip(download_dir, object_key) == False:
                    return False
            if reset:
                minio_client.delete_object(Bucket=bucket_name, Key=object_key)
                print(f"Object deleted from bucket: {object_key}")
    except Exception as e:
        print(f"Error during download of objects from MinIO: {e}")
        return False
    return True


def download_file_by_patterns_from_buckets(minio_client, download_dir, buckets_name, patterns, reset=False):
    for bucket_name in buckets_name:
        if download_file_by_patterns(minio_client, download_dir, bucket_name, patterns, reset=reset) == False:
             return False
    return True

import zipfile

def unzip(folder, fileName):
    try:
        zip_file_path = os.path.join(folder, fileName)
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            zip_ref.extractall(folder)
        print(f"File extracted: {zip_file_path}")
        return True
    except Exception as e:
        print(f"Error during extraction of {zip_file_path}: {e}")
        return False

def download_files_excel(minio_client, download_dir, bucket_name, reset=False):
    try:
        objects_list = minio_client.list_objects(Bucket=bucket_name)
        for obj in objects_list.get('Contents', []):
            object_key = obj['Key']

            if not object_key.endswith('.xlsx') and not object_key.endswith('.zip'):
                continue
            object_path = os.path.join(download_dir, object_key)
            minio_client.download_file(bucket_name, object_key, object_path)
            print(f"Download completed: {object_path} from bucket {bucket_name}")
            if object_key.endswith('.zip'):
                if unzip(download_dir, object_key) == False:
                    return False
            if reset:
                minio_client.delete_object(Bucket=bucket_name, Key=object_key)
                print(f"Object deleted from bucket: {object_key}")
    except Exception as e:
        print(f"Error during download of objects from MinIO: {e}")
        return False
    return True