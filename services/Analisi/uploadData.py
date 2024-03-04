
import os

def upload_file_to_minio(minio_client,file_path, bucket_name, object_name, remove=True):
    # Uploading file to MinIO bucket
    try:

        with open(file_path, 'rb') as file_data:
            minio_client.put_object(
                Bucket=bucket_name,
                Key=object_name,
                Body=file_data
            )
        print(f"File {object_name} caricato")
        #da vedere se funziona
        if remove:
            os.remove(file_path)
        return True
    except Exception as e:
        print(f"Error during upload of files: {e}")
        return False


#file path (directory where the file is) all files in same dir
def upload_files_to_minio(minio_client, path, bucket, files, remove=True):
    for file in files:
        file_path=path+"/"+file
        if upload_file_to_minio(minio_client, file_path, bucket, file, remove=remove) == False:
            return False
    return True



def remove_objects_from_minio(minio_client,bucket_name, patterns):
    if len(patterns)==0:
        return True
    # List objects in the bucket
    try:
        objects_list = minio_client.list_objects(Bucket=bucket_name)
        for obj in objects_list.get('Contents', []):
            object_key = obj['Key']
            # Check if the object matches any of the patterns
            if all(pattern not in object_key for pattern in patterns):
                continue
            minio_client.delete_object(Bucket=bucket_name, Key=object_key)
            print(f"Object deleted from MinIO bucket {bucket_name}: {object_key}")
    except Exception as e:
        print(f"Error removing objects from MinIO: {e}")
        return False
    return True


def create_bucket(minio_client, buckets_name):
    try:
        for bucket_name in buckets_name:
            minio_client.create_bucket(Bucket=bucket_name)
            print(f"Bucket {bucket_name} created.")
    except Exception as e:
        print(f"Error during the creation of bucket {bucket_name}: {str(e)}")

