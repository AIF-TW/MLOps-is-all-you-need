source ../../../mlops-sys/ml_experimenter/.env.local

# 下載資料集MNIST.zip
gdown "https://drive.google.com/file/d/1296F7Fa2hZy_2cImet8S-HlZhcWqOdwa/view?usp=sharing" -O MNIST.zip --fuzzy
# 若無法下載，可以使用瀏覽器打開以上連結來手動下載

mkdir data
if [ -e data/MNIST ]; then
    echo 'data/MNIST/ exists.'
else
    unzip MNIST.zip -d data/
fi

# 製作v1.0的訓練資料，並讓DVC開始追蹤
git init  # 需要先以git對資料夾進行初始化
dvc init  # DVC對資路夾進行初始化
dvc add data  # 將MNIST資料夾以DVC追蹤
git add data.dvc .gitignore
git commit -m "First version of training data."  # 以git對.dvc進行版控
git tag -a "v1.0" -m "Created dataset."  # 建立標籤，未來要重回某個版本時比較方便 

# ----------- dvc remote setting -----------
dvc remote add -f minio_s3 $MINIO_S3_PROJECT_BUCKET/dvc_remote/  # remote為自定義的遠端名稱
dvc remote modify minio_s3 endpointurl $MLFLOW_S3_ENDPOINT_URL
dvc remote modify minio_s3 access_key_id $AWS_ACCESS_KEY_ID
dvc remote modify minio_s3 secret_access_key $AWS_SECRET_ACCESS_KEY
# ------------------------------------------

dvc push -r minio_s3  # 推送至minio_s3

# 將更多訓練資料加入train/
for ((digit=0; digit<=9; digit++))
do
    mv ./data/MNIST/train_v2/$digit/* ./data/MNIST/train/$digit/
done
rm -r ./data/MNIST/train_v2/

# 製作v2.0的訓練資料
dvc add data
git add data.dvc
git commit -m "Add some images"
git tag -a "v2.0" -m "More images added."
dvc push -r minio_s3
#git push  # 如果有遠端的git repo才需要執行

python upload_dvc_file_to_minio.py  # 將MNIST.dvc上傳至MinIO

cp -r .git ../flow
