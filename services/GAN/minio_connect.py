import boto3
import os
def connect():
	try:
	    minio_client = boto3.client(
	        's3',
	        endpoint_url=os.getenv('MINIO_SERVER_ADDRESS',"http://minio:9000"),
	        aws_access_key_id=os.getenv('MINIO_ROOT_USER',"ste"),
	        aws_secret_access_key=os.getenv('MINIO_ROOT_PASSWORD',"steflois")
	    )
	except Exception as e:
	    raise Exception(f"Errore in fase di connessione {str(e)}")
	return minio_client