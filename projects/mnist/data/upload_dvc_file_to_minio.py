import os
from dotenv import load_dotenv
from minio import Minio

load_dotenv()

client = Minio(
   endpoint='localhost:9000', 
   access_key=os.getenv('MINIO_ROOT_USER'), 
   secret_key=os.getenv('MINIO_ROOT_PASSWORD'), 
   secure=False
)

def main():
    bucket_name = f"{os.getenv('DVC_BUCKET_NAME')}"
    found = client.bucket_exists(bucket_name)
    if not found:
       client.make_bucket(bucket_name)
       
    client.fput_object(bucket_name, f"{os.getenv('PROJECT_NAME')}/MNIST.dvc", './MNIST.dvc',)
    print("MNIST.dvc is successfully uploaded to bucket")

if __name__ == '__main__':
   main()
