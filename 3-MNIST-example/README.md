# 以手寫數字資料集實作系統建置與執行實驗
這份範例是透過手寫數字辨識模型的開發，實際操作以下步驟：
- 進行資料版本控制
- 追蹤模型的訓練結果
- 對模型再訓練進行自動化排程

## 目錄
- [使用工具](#使用工具)
- [環境需求](#運行環境需求)
- [資料夾結構](#資料夾結構)
- [執行步驟](#執行步驟)
    - [1. 資料版本控制](#1-資料版本控制)
    - [2. 實驗性的訓練](#2-實驗性的訓練)
    - [3. 模型的定期再訓練](#3-模型的定期再訓練)
- [工作資料夾說明](#工作料夾說明)

## 使用工具
* [MinIO](https://min.io)：提供[物件儲存](https://aws.amazon.com/tw/what-is/object-storage/)服務。
* [Prefect](https://www.prefect.io)：把定期執行的任務進行排程，並透過[Prefect Agent](https://docs.prefect.io/latest/concepts/agents/)執行，使用者能隨時透過其UI監控每個工作的狀態。
* [MLflow](https://mlflow.org)：MLflow能用來追蹤模型、紀錄實驗結果，以及做到模型版本控制。
* [Data Version Control (DVC)](https://dvc.org)：DVC是著名的開源資料版本控制工具，操作邏輯與[Git](https://git-scm.com)類似，可支援S3、Google Drive以及其他常見的雲端服務。

## 環境需求
必須完成[`0-Quick-Install`](/0-Quick-Install/)的所有步驟，並確認以下服務正常運作：
* MinIO: [`http://localhost:9001/`](http://localhost:9001/)
* Prefect: [`http://localhost:4200/`](http://localhost:4200/)
* MLflow: [`http://localhost:5050/`](http://localhost:5050/)

## 資料夾結構
這份範例主要有2個資料夾：
* `flow_agent/`：建立負責執行排程的Prefect Agent。
* `flow_schedualer/`：包含建立排程以及模型訓練相關的檔案。

<details>
<summary>詳細的資料夾結構</summary>

```
3-MNIST-example
├── README.md
├── flow_agent
│   └── flow_agent_mnist_cpu
│       ├── Dockerfile
│       ├── docker-compose.yml
│       ├── requirements.txt
│       └── requirements_sys.txt
├── flow_scheduler
│   ├── flow_scheduler
│   │   ├── Dockerfile
│   │   ├── docker-compose.yml
│   │   ├── requirements_sys.txt
│   │   └── setup.py
│   └── flows_mnist
│       ├── config
│       │   ├── dataset.yml
│       │   ├── flow.yml
│       │   └── hyp.yml
│       ├── data
│       │   ├── MNIST.zip
│       │   ├── data_version.sh
│       │   └── expand_train_data.py
│       ├── flow.py
│       ├── mnist.ipynb
│       └── requirements.txt
└── png
```
</details>

## 執行步驟
### 1. 資料版本控制
在`flow_scheduler/flows_mnist/data/`執行[`data_version.sh`](./flow_scheduler/flows_mnist/data/data_version.sh)，製作第1與第2版的資料，並推送到remote，讓後續步驟能夠使用：
````shell
cd MLOps-is-all-you-need/3-MNIST-example/flow_scheduler/flows_mnist/data/
. ./data_version.sh
````
`data_version.sh`執行的動作有以下幾點，可以展開來查看說明：
<details>
  <summary>將<code>MNIST/</code>資料夾加入追蹤，並建立v1.0的資料集</summary>

````shell
cd flow_scheduler/flows_mnist/data/
git init  # 要使用DVC來做資料版本控制，需要先以git對資料夾進行初始化
dvc init
dvc add MNIST  # MNIST為資料所在的資料夾名稱
git add .gitignore MNIST.dvc  # git add 後面的檔案順序不影響結果
# 執行dvc add MNIST後DVC也會在終端機上輸出這一條訊息，並且告訴使用者可以直接複製來執行
git commit -m "First version of training data."  # 以git對.dvc進行版控，製作第一個提交
git tag -a "v1.0" -m "Created MNIST."  # 建立標籤，未來要重回某個版本時比較方便
````
</details>

<details>
  <summary>推送至remote</summary>

````shell
dvc remote add remote s3://dvc/  # dvc add 後面接的「remote」是自定義的名稱
dvc remote modify remote endpointurl http://localhost:9000
export AWS_ACCESS_KEY_ID=admin
export AWS_SECRET_ACCESS_KEY=adminsecretkey
dvc push -r remote  # 把這次的更動推送上到名為remote的遠端上
````

要在其他設備或容器下載資料集的話，只要取得`MNIST.dvc`，執行以下程式碼即可：
````commandline
export AWS_ACCESS_KEY_ID=[MinIO的帳號]
export AWS_SECRET_ACCESS_KEY=[MinIO的密碼]
dvc remote add remote [DVC remote路徑]
dvc remote modify remote endpointurl [MinIO endpoint URL]
dvc pull --remote remote
````
</details>

<details>
  <summary>增加一些資料，作為v2.0的資料集</summary>

````shell
dvc add MNIST
git add MNIST.dvc
git commit -m "Add some images"
git tag -a "v2.0" -m "v2.0, more images"
dvc push -r remote  # 把這次的更動Push上去
# git push  # 如果有git repo可以執行
````
</details>

### 2. 實驗性的訓練
執行[`flow_scheduler/flows_mnist/mnist.ipynb`](/3-MNIST-example/flow_scheduler/flows_mnist/mnist.ipynb)的所有步驟，完成模型訓練與追蹤。

待`mnist.ipynb`全部執行完，就可以進入MLflow UI檢視剛才紀錄的實驗結果，進入MLflow UI後，於畫面左側實驗名稱點選「MNIST」，進入到這個實驗的頁面：
![image](./png/MLflow_exp.png)

進入實驗後，點選某一次的執行即可檢視結果：
![image](./png/MLflow_run.png)
> 可以展開左側「Parameters」檢視模型訓練時的超參數，或是展開「Metrics」確認模型指標。

### 3. 模型的定期再訓練
#### 3.1. 製作自動化排程
執行以下指令將排程資料上傳到Prefect伺服器：
````shell
cd MLOps-is-all-you-need/3-MNIST-example/flow_schedualer/
docker compose up --build
````

這個步驟的目的是將工作資料夾（就是[`flows_mnist`](./flow_scheduler/flows_mnist/)）上傳到Prefect伺服器。當容器成功建立，會看到包含以下文字的訊息：
````
flow_scheduler  | Created work pool 'cpu_pool'.
flow_scheduler  | Found flow 'MNIST'
flow_scheduler  | Deployment YAML created at '/root/flows/main-deployment.yaml'.
flow_scheduler  | Successfully uploaded 56 files to s3://prefect/main/model_training
flow_scheduler  | Deployment 'MNIST/model_training' successfully created with id 
flow_scheduler  | '86d20e16-9f72-46f1-b2d0-83da39e8b9d2'.  # 在你的環境啟動時，顯示的id可能和本範例不同
flow_scheduler  | 
flow_scheduler  | To execute flow runs from this deployment, start an agent that pulls work from 
flow_scheduler  | the 'cpu_pool' work pool:
flow_scheduler  | 
flow_scheduler  | $ prefect agent start -p 'cpu_pool'
flow_scheduler exited with code 0
````
> 訊息顯示排程已上傳至Prefect伺服器，正等待Prefect Agent來執行這個排程，接下來就要啟動另一個容器來建立Prefect Agent。

#### 3.2. 建立Prefect Agent來執行排程
啟動Prefect Agent：
````shell
cd MLOps-is-all-you-need/3-MNIST-example/flow_agent/flow_agent_pool_ml_cpu/
docker compose up --build
````
當容器成功建立，會看到包含以下文字的訊息：
````
flow_agent_cpu_pool_mnist_cpu  | Starting v2.10.9 agent connected to http://prefect_server:4200/api...
flow_agent_cpu_pool_mnist_cpu  | 
flow_agent_cpu_pool_mnist_cpu  |   ___ ___ ___ ___ ___ ___ _____     _   ___ ___ _  _ _____
flow_agent_cpu_pool_mnist_cpu  |  | _ \ _ \ __| __| __/ __|_   _|   /_\ / __| __| \| |_   _|
flow_agent_cpu_pool_mnist_cpu  |  |  _/   / _|| _|| _| (__  | |    / _ \ (_ | _|| .` | | |
flow_agent_cpu_pool_mnist_cpu  |  |_| |_|_\___|_| |___\___| |_|   /_/ \_\___|___|_|\_| |_|
flow_agent_cpu_pool_mnist_cpu  | 
flow_agent_cpu_pool_mnist_cpu  | 
flow_agent_cpu_pool_mnist_cpu  | 
flow_agent_cpu_pool_mnist_cpu  | Agent started! Looking for work from work pool 'cpu_pool'...

````

Prefect Agent會依照排程指定的時間自Prefect伺服器下載工作資料夾（`flow_scheduler/flows_mnist`），並執行指定的Python檔（`flow.py`），對工作資料夾的說明。

<details>
    <summary>Prefect的使用範例</summary>

範例中會用到以下這兩項常用功能：
* [`task`](https://docs.prefect.io/latest/concepts/tasks/)：用來裝飾`main`會執行到的函式，可自訂這些任務的名稱、重新嘗試次數、重新嘗試的等待時間。
* [`flow`](https://docs.prefect.io/latest/concepts/flows/)：用來裝飾`main`函式，同樣能設定重新嘗試的次數、等待時間，以及最長的執行時間限制等等。

````python
import mlflow
from prefect import flow, task

@task(name='Model training')  # 以@task裝飾，代表是流程中的一個任務
def model_training():
    ...

@flow(name='MNIST')  # 以@flow裝飾，代表是工作流程
def main():
    model_training()
    ...

if __name__ == '__main__':
    main()
````
其中的`main`與`model_training`函式分別以`@flow`與`@task`裝飾，代表兩者分別是工作流程以及流程中的任務。更多詳細使用方式可以參考[Prefect的官方教學](https://docs.prefect.io/latest/tutorialc/)。

</details>

> 此範例以CPU版進行說明，若要使用GPU版，可參考[4-GPU-agent](/4-GPU-agent/)。

現在我們已經設定好排程，也建立好負責執行程式碼的Agent，接著進入Prefect UI，在左側欄選擇「Flows」，確認是否出現「MNIST」
![image](./png/Prefect_UI_check_flows.png)

由於目前還沒到排程的指定時間，我們也可以強制執行一次。展開「MNIST」，到「model_training」卡片的右上角點選選項按鈕，點一下「Quick run」即可快速執行一次。
![image](./png/Prefect_quick_run.png)

接著可以在左側欄位點選「Flow Runs」，點選剛才開始執行的任務（任務名稱為Prefect隨機生成）
![image](./png/Prefect_go_to_flow_run.png)

就可以監控任務執行的狀態
![image](./png/Prefect_running.png)
