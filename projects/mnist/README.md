# 以MNIST實作系統建置與執行實驗
這份範例是透過手寫數字辨識模型的開發，實際操作以下步驟：
- 進行資料版本控制
- 在模型實驗階段，訓練模型並追蹤模型結果
- 模型穩定後，對模型的定期再訓練進行自動化排程
- 運用CPU和GPU資源來執行排程

## 目錄
- [使用工具](#使用工具)
- [環境需求](#運行環境需求)
- [工作資料夾結構](#工作資料夾結構)
- [執行步驟](#執行步驟)
    - [資料版本控制](#1-資料版本控制)
    - [實驗性的訓練](#2-實驗性的訓練)
    - [模型定期訓練的排程](#3-模型定期訓練的排程)
    - [測試](#4-測試)

## 使用工具
* [MinIO](https://min.io)：提供[物件儲存](https://aws.amazon.com/tw/what-is/object-storage/)服務。
* [Prefect](https://www.prefect.io)：把定期執行的任務進行排程，並透過[Prefect Agent](https://docs.prefect.io/latest/concepts/agents/)執行，使用者能隨時透過其UI監控每個工作的狀態。
* [MLflow](https://mlflow.org)：MLflow能用來追蹤模型、紀錄實驗結果，以及做到模型版本控制。
* [Data Version Control (DVC)](https://dvc.org)：DVC是著名的開源資料版本控制工具，操作邏輯與[Git](https://git-scm.com)類似。

## 環境需求
1. 需要確認以下服務正常運作：
* MinIO
* Prefect
* MLflow

2. 此範例的所有步驟都需要在[快速安裝](/wiki/0-quick-install/README.md)建立的環境`mlops`操作。如果尚未進到`mlops`環境，可以在終端機執行`conda activate mlops`來進入環境。

## 工作資料夾結構
```
mnist
├── README.md
├── dev
│   ├── data
│   │   ├── MNIST.zip
│   │   ├── data_version.sh
│   │   └── upload_dvc_file_to_minio.py
│   ├── mnist.py
│   └── requirements.txt
├── flow
│   ├── config
│   │   ├── dataset.yml
│   │   ├── flow.yml
│   │   └── hyp.yml
│   ├── flow.py
│   └── requirements.txt
└── img
```
* `dev/`: 開發階段的相關檔案
  - `data/`: 放置資料集與版本控制檔案
    - `MNIST.zip`: MNIST資料集，解壓縮後會產生`MNIST/`資料夾，內容為訓練資料與測試資料
    - `data_version.sh`: 用來完成資料版本控制的Shell檔
  - `mnist.py`: 執行模型訓練任務的Python檔
  - `requirements.txt`: 執行任務所需的套件清單

* `flow/`: 排程階段的相關檔案
  - `config/`: 放置任務的各項設定值
    - `dataset.yaml`: 資料集相關設定，例如資料的路徑
    - `flow.yaml`: 排程相關設定
    - `hyp.yaml`: 模型超參數設定
  - `flow.py`: 要讓Prefect自動執行的Python檔

## 執行步驟
### 1. 資料版本控制
在`MLOps-is-all-you-need/projects/mnist/dev/data`路徑執行`data_version.sh`：
````shell
. ./data_version.sh
````
執行`data_version.sh`目的是為了使用DVC來對訓練資料進行版本控制，執行的動作有以下幾點，可以展開來查看較詳細的說明：
<details>
  <summary>將<code>MNIST/</code>資料夾加入追蹤，建立v1.0的資料集</summary>

````shell
if [ -e MNIST ]; then
    echo 'MNIST/ exists.'
else
    unzip MNIST.zip
fi

# 製作v1.0的訓練資料，並讓DVC開始追蹤
git init  # 需要先以git對資料夾進行初始化
dvc init  # DVC對資路夾進行初始化
dvc add MNIST  # 將MNIST資料夾以DVC追蹤
git add .gitignore MNIST.dvc  # git add 後面的檔案順序可對調
git commit -m "First version of training data."  # 以git對.dvc進行版控
git tag -a "v1.0" -m "Created MNIST."  # 建立標籤，未來要重回某個版本時比較方便
````
</details>

<details>
  <summary>推送至DVC remote</summary>

````shell
dvc remote add -f minio_s3 s3://$DVC_BUCKET_NAME/$PROJECT_NAME  # remote為自定義的遠端名稱
dvc remote modify minio_s3 endpointurl $MLFLOW_S3_ENDPOINT_URL
dvc push -r minio_s3  # 推送至minio_s3
````

要在其他設備或容器下載資料集的話，只要取得`MNIST.dvc`，執行以下程式碼即可（必須確認環境變數已設定好）：
````commandline
dvc remote add remote [DVC_REMOTE]
dvc remote modify remote endpointurl [ENDPOINT_URL]
dvc pull --remote remote
````
</details>

<details>
  <summary>增加一些資料，作為v2.0的資料集，同樣也推送到DVC remote</summary>

````shell
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

python3 upload_dvc_file_to_minio.py  # 將MNIST.dvc上傳至MinIO
````
</details>

### 2. 實驗性的訓練
````shell
cd MLOps-is-all-you-need/projects/mnist/dev
python3 mnist.py
````
執行`MLOps-is-all-you-need/projects/mnist/mnist.py`的所有步驟，完成一次模型訓練並且用MLflow追蹤訓練結果。

<details>
<summary>
如何在MLflow UI檢視實驗結果
</summary>

進入MLflow UI後，於畫面左側實驗名稱點選「MNIST」，進入到這個實驗的頁面：
![image](./img/MLflow_exp.png)

進入實驗後，點選某一次的執行即可檢視結果：
![image](./img/MLflow_run.png)
> 可以展開左側「Parameters」檢視模型訓練時的超參數，或是展開「Metrics」確認模型指標。

</details>

### 3. 模型定期訓練的排程
#### 3.1. 將排程上傳到Prefect伺服器
打開`MLOps-is-all-you-need/mlops-sys/flow_scheduler/.env.local`，更改以下設定：
```
# FLOW_DIR = '../../flows/example_flow' # project directory of your flow.py
改為
FLOW_DIR = '../../flows/flow-mnist' # project directory of your flow.py
```

執行以下指令將排程資料上傳到Prefect伺服器：
````shell
cd MLOps-is-all-you-need/mlops-sys/flow_scheduler/
docker compose -f docker-compose-local.yml --env-file ./.env.local up --build
````

這個步驟的目的是將工作資料夾（就是`MLOps-is-all-you-need/projects/mnist/flow/`）上傳到Prefect伺服器，並且製作排程。當容器成功建立，會看到包含以下文字的訊息：
````
 ✔ Container flow_scheduler  Recreated
flow_scheduler  | Work pool named 'mnist-cpu' already exists. Please try creating your work pool 
flow_scheduler  | again with a different name.
flow_scheduler  | Found flow 'MNIST'
flow_scheduler  | Default '.prefectignore' file written to /root/flows/.prefectignore
flow_scheduler  | Deployment YAML created at '/root/flows/main-deployment.yaml'.
flow_scheduler  | Successfully uploaded 8 files to s3://prefect/main/model_training
flow_scheduler  | Deployment 'MNIST/model_training' successfully created with id 
flow_scheduler  | '476b5fc2-cb78-4e32-99ea-961ee84873a0'.  # 在你的環境執行時，可能會看到不同的id
flow_scheduler  | 
flow_scheduler  | To execute flow runs from this deployment, start an agent that pulls work from 
flow_scheduler  | the 'mnist-cpu' work pool:
flow_scheduler  | 
flow_scheduler  | $ prefect agent start -p 'mnist-cpu'
flow_scheduler exited with code 0
````
> 訊息顯示排程已上傳至Prefect伺服器，正等待Prefect Agent來執行這個排程，接下來就要啟動另一個容器來建立Prefect Agent。

#### 3.2. 建立Prefect CPU Agent來執行排程
啟動Prefect CPU Agent：
````shell
cd MLOps-is-all-you-need/mlops-sys/flow_agent/cpu_pool_mnist_local_cpu/
docker compose up --build -d
````
> 在`docker compose up`後加上`-d`，就能讓Docker不佔用一個終端機視窗。

Prefect Agent會依照排程指定的時間自Prefect伺服器下載工作資料夾，並執行指定的Python檔，不過要注意的是此Python檔必須配合[Prefect規定的方式](https://docs.prefect.io/latest/tutorial/flows/)撰寫。

#### 3.3. 建立Prefect GPU Agent排程
如果電腦配有NVIDIA GPU，可以執行這個段落來建立GPU Agent。
**需要先確認[CUDA](https://www.nvidia.com/zh-tw/geforce/technologies/cuda/)已設定好，且CUDA Version為11.6以上。**
<details>
<summary>確認方式：</summary>

  在終端機執行```nvidia-smi```來開啟[NVIDIA System Management Interface](https://developer.nvidia.com/nvidia-system-management-interface)，假如能看到所有已裝備的GPU以及CUDA版本，如下列範例，就代表所需的驅動都已裝好。如果未能看到設備安裝的GPU，可能是因為沒有正確安裝驅動程式。
  ````shell
  (mlops) aif@aif_mlops:~$ nvidia-smi
  Thu Jan 25 14:46:01 2024       
  +-----------------------------------------------------------------------------+
  | NVIDIA-SMI 525.105.17   Driver Version: 525.105.17   CUDA Version: 12.0     |
  |-------------------------------+----------------------+----------------------+
  | GPU  Name        Persistence-M| Bus-Id        Disp.A | Volatile Uncorr. ECC |
  | Fan  Temp  Perf  Pwr:Usage/Cap|         Memory-Usage | GPU-Util  Compute M. |
  |                               |                      |               MIG M. |
  |===============================+======================+======================|
  |   0  Tesla V100-SXM2...  Off  | 00000000:00:05.0 Off |                    0 |
  | N/A   28C    P0    53W / 300W |      0MiB / 32768MiB |      0%      Default |
  |                               |                      |                  N/A |
  +-------------------------------+----------------------+----------------------+
  |   1  Tesla V100-SXM2...  Off  | 00000000:00:06.0 Off |                    0 |
  | N/A   26C    P0    53W / 300W |      0MiB / 32768MiB |      0%      Default |
  |                               |                      |                  N/A |
  +-------------------------------+----------------------+----------------------+
                                                                                
  +-----------------------------------------------------------------------------+
  | Processes:                                                                  |
  |  GPU   GI   CI        PID   Type   Process name                  GPU Memory |
  |        ID   ID                                                   Usage      |
  |=============================================================================|
  |  No running processes found                                                 |
  +-----------------------------------------------------------------------------+
  (mlops) aif@aif_mlops:~$ 
 
  ````

</details>

打開`MLOps-is-all-you-need/projects/mnist/flow/config/flow.yml`，更改以下3個設定並存檔：
```
將原先的
deploy_name: model_training-cpu  # 目的，如daliy_model、data_update

pool_name: mnist-cpu  # 要調用的運算資源
queue_name: mnist-cpu  # 專案名稱
改為
deploy_name: model_training-gpu  # 目的，如daliy_model、data_update

pool_name: mnist-gpu  # 要調用的運算資源
queue_name: mnist-gpu  # 專案名稱
```

執行以下指令將排程資料上傳到Prefect伺服器（指令與Prefect CPU Agent相同）：
````shell
cd MLOps-is-all-you-need/mlops-sys/flow_scheduler/
docker compose -f docker-compose-local.yml --env-file ./.env.local up --build
````

啟動Prefect GPU Agent：
````shell
cd MLOps-is-all-you-need/mlops-sys/flow_agent/mnist-gpu_mnist_single_gpu/
docker compose up --build -d
````

### 4. 測試
在排程開始執行前我們需要進行測試，來確認排程可以正常執行，這邊以CPU Agent為例，。

進入Prefect UI，在左側欄選擇「Flows」，確認畫面中是否出現「MNIST」
![image](./img/Prefect_UI_check_flows.png)

展開「MNIST」，到「model_training-cpu」卡片的右上角點選選項（ ⋮ ）按鈕，點一下「Quick run」來快速執行一次排程，畫面右下角會立即顯示這個任務的名稱（Prefect會為每次任務隨機指派一個特定名稱）。
![image](./img/Prefect_quick_run.png)

接著在左側欄位點選「Flow Runs」，點選任務名稱
![image](./img/Prefect_go_to_flow_run.png)

就可以監控任務執行的狀態，可以看到各個任務的執行狀態都清楚的顯示出來
![image](./img/Prefect_running.png)
