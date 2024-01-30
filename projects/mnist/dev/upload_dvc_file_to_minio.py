import os
from dotenv import load_dotenv
from minio import Minio

load_dotenv('../../../mlops-sys/ml_experimenter/.env.local')

client = Minio(
   endpoint=os.getenv('MLFLOW_S3_ENDPOINT_URL').replace('http://', ''),
   access_key=os.getenv('MINIO_ROOT_USER'), 
   secret_key=os.getenv('MINIO_ROOT_PASSWORD'), 
   secure=False
)

def main():
    bucket_name = f"{os.getenv('DVC_BUCKET_NAME')}"
    found = client.bucket_exists(bucket_name)
    if not found:
       client.make_bucket(bucket_name)
       
    client.fput_object(bucket_name, f"{os.getenv('PROJECT_NAME')}/dot_dvc_file/data.dvc", './data.dvc',)

if __name__ == '__main__':
   main()
