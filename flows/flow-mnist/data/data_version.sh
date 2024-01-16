set -a            
source ../.env  # 設定環境變數
set +a

unzip MNIST.zip  # 解壓縮MNIST.zip，如果已經解壓縮過，這條可以註解掉

# 製作v1.0的訓練資料，並讓DVC開始追蹤
git init  # 需要先以git對資料夾進行初始化
dvc init  # DVC對資路夾進行初始化
dvc add MNIST  # 將MNIST資料夾以DVC追蹤
git add .gitignore MNIST.dvc  # git add 後面的檔案順序可對調
git commit -m "First version of training data."  # 以git對.dvc進行版控
git tag -a "v1.0" -m "Created MNIST."  # 建立標籤，未來要重回某個版本時比較方便

export AWS_ACCESS_KEY_ID=$MINIO_ROOT_USER
export AWS_SECRET_ACCESS_KEY=$MINIO_ROOT_PASSWORD

echo "Pushing to s3://$DVC_BUCKET_NAME/$PROJECT_NAME/"
dvc remote add -f minio_s3 s3://$DVC_BUCKET_NAME/$PROJECT_NAME/  # remote為自定義的遠端名稱
dvc remote modify minio_s3 endpointurl $MLFLOW_S3_ENDPOINT_URL
dvc push -r minio_s3  # 推送至minio_s3

# 將更多訓練資料加入train/
for ((digit=0; digit<=9; digit++))
do
    mv ./MNIST/train_v2/$digit/* ./MNIST/train/$digit/
done
rm -r ./MNIST/train_v2/

# 製作v2.0的訓練資料
dvc add MNIST
git add MNIST.dvc
git commit -m "Add some images"
git tag -a "v2.0" -m "More images added."
dvc push -r minio_s3
#git push  # 如果有遠端的git repo才需要執行