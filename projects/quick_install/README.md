# 快速安裝
此章節旨在說明如何快速安裝 MLOps 系統。本系統包含 4 個功能/服務，分別是
1. 伺服器 `server`：使用 MLflow 與 Prefect 分別提供模型版本控制與排程控制的服務
2. 開發環境 `ml_experimenter`：建立開發環境需要的基本環境變數與套件清單
3. 工作流程的排程功能 `flow_scheduler`：將排程專案上傳到 `server` 的功能
4. 工作流程的執行服務`flow_agent`：執行 `server` 指定排程任務的服務

本文提供`多機模式`與`單機模式`兩種部署模式。使用者如果是多人開發團隊，可以將上述 4 個功能/服務分別部署在不同電腦中（`多機模式`），本文將以 `電腦1`、`電腦2`、`電腦3`、`電腦4`指稱 4 個功能/服務分別部署的電腦。而使用者如果是單人使用或是以測試為目的，可以將上述 4 個功能/服務部署在同一台電腦（`單機模式`）。

除此之外，本文針對`工作流程的排程功能`也提供 CPU 和 GPU 兩個版本，使用者可以根據排程任務中的模型需求，選擇對應的版本。

更多 MLOps 系統的知識請參考 [<AI 專案開發一定要用 MLOps 嗎？從專案流程看起>](https://edge.aif.tw/about-mlops-project-flow)。

## 事前準備
> 如果是 `多機模式`，請在所有電腦都執行下列步驟

1. 請先安裝需求套件： [`Git`](https://git-scm.com/book/zh-tw/v2/%E9%96%8B%E5%A7%8B-Git-%E5%AE%89%E8%A3%9D%E6%95%99%E5%AD%B8) 、 [`Docker`](https://www.docker.com/products/docker-desktop/) 、 [`Conda`](https://conda.io/projects/conda/en/latest/user-guide/install/index.html#)
    - 如果 `工作流程的執行服務` 需要使用 GPU，請在該電腦安裝 [`NVIDIA Container Toolkit`](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html)

> 註：如果是 Windows作業系統，建議使用 Bash 執行此章節的指令，比如使用 `Git Bash` 執行。 `Git Bash` 會在下載 `Git` 套件的時候一併下載，使用方式請參考 [如何在VScode 使用 git bash](https://code.visualstudio.com/docs/sourcecontrol/intro-to-git#_git-bash-on-windows)。

2. 開啟終端機，在根目錄下載此專案
    > 如果不在根目錄下載請特別注意檔案路徑，後續內容需要自行調整檔案路徑
    ```
    git clone https://github.com/AIF-TW/MLOps-is-all-you-need.git ~/MLOps-is-all-you-need
    ```
3. 進入此專案主要功能的資料夾
    ```
    cd ~/MLOps-is-all-you-need/mlops-sys
    ```
    <details><summary>主要功能檔案結構</summary>
    <p>

    > 請注意有些顯示界面會隱藏 `.env` 和 `.env.local` 檔案
    ```
    ./mlops-sys
    ├── flow_agent
    │   ├── default-agent-pool_ml_distributed_cpu
    │   │   ├── .env
    │   │   ├── Dockerfile
    │   │   ├── docker-compose.yml
    │   │   ├── requirements.txt
    │   │   └── requirements_sys.txt
    │   ├── default-agent-pool_ml_distributed_gpu
    │   │   ├── .env
    │   │   ├── Dockerfile
    │   │   ├── docker-compose.yml
    │   │   ├── requirements.txt
    │   │   └── requirements_sys.txt
    │   ├── default-agent-pool_ml_local_cpu
    │   │   ├── .env
    │   │   ├── Dockerfile
    │   │   ├── docker-compose.yml
    │   │   ├── requirements.txt
    │   │   └── requirements_sys.txt
    │   ├── default-agent-pool_ml_local_gpu
    │   │   ├── .env
    │   │   ├── Dockerfile
    │   │   ├── docker-compose.yml
    │   │   ├── requirements.txt
    │   │   └── requirements_sys.txt
    │   ├── flow_agent_mnist_cpu
    │   │   ├── .env
    │   │   ├── Dockerfile
    │   │   ├── docker-compose.yml
    │   │   ├── requirements.txt
    │   │   └── requirements_sys.txt
    │   ├── flow_agent_pool_ml_cpu
    │   │   ├── Dockerfile
    │   │   ├── docker-compose.yml
    │   │   ├── requirements.txt
    │   │   └── requirements_sys.txt
    │   ├── flow_agent_pool_ml_gpu_0
    │   │   ├── Dockerfile
    │   │   ├── docker-compose.yml
    │   │   ├── requirements.txt
    │   │   └── requirements_sys.txt
    │   └── flow_agent_pool_ml_gpu_1
    │       ├── Dockerfile
    │       ├── docker-compose.yml
    │       ├── requirements.txt
    │       └── requirements_sys.txt
    ├── flow_scheduler
    │   ├── .env
    │   ├── .env.local
    │   ├── Dockerfile
    │   ├── docker-compose-local.yml
    │   ├── docker-compose.yml
    │   ├── requirements_sys.txt
    │   └── setup.py
    ├── ml_experimenter
    │   ├── .env
    │   ├── .env.local
    │   └── requirements_sys.txt
    └── server
        ├── .env
        ├── .env.local
        ├── docker-compose-local.yml
        ├── docker-compose.yml
        ├── init.sh
        └── prefect_setting_s3.py
    ```

    </p>
    </details>

## 開始安裝
請依序完成以下4個服務/功能的安裝。

### 伺服器 Server
> `多機模式` 請在 `電腦1` 執行此段落

> 請開啟新的終端機環境執行本小節的指令

1. [單機模式跳過此步驟] 多機模式請先取得此電腦的 `預設電腦IP`，此 IP 將作為其他服務/功能連線到 `伺服器 Server` 的依據，本章節接下來將以 `SERVER_IP` 指稱。

    <details><summary>取得預設電腦IP的方法參考</summary>
    <p>

    ```
    # 在終端機運行

    # linux
    ifconfig $(ip route | awk '/default/ {print $5}') | awk '/inet/ {print $2}' | head -n 2

    # mac
    ifconfig $(netstat -rn | awk '/default/ {print $4}' | head -n 1) | awk '/inet/ {print $2}'

    # linux/mac 輸出範例
    # fe80::f1e6:5c46:af01:7b34   --> IPv6
    # 172.16.110.13               --> IPv4 ， 請使用這個作為 MASTER_IP

    # windows
    ipconfig

    # windows 輸出範例
    # 無線區域網路介面卡 Wi-Fi:
    #    連線特定 DNS 尾碼 . . . . . . . . :
    #    連結-本機 IPv6 位址 . . . . . . . : fe80::4bdb:1045:4d34:f1a4%13
    #    IPv4 位址 . . . . . . . . . . . . : 172.16.110.107  --> 請使用有「預設閘道」的 IPv4 作為 MASTER_IP
    #    子網路遮罩 . . . . . . . . . . . .: 255.255.255.0    
    #    預設閘道 . . . . . . . . . . . . .: 172.16.110.1
    ```

    </p>
    </details>


2. [單機模式跳過此步驟] 多機模式需將 `SERVER_IP` 設定寫進 [`mlops-sys/server/.env`](../../mlops-sys/server/.env)
    ```
    SERVER_IP= 'YOUR_SERVER_IP' # 取消註解，並填入 SERVER_IP 及存檔   
    ```

3. 進入到 `server` 資料夾，並啟動伺服器服務
    ```
    # 單機模式
    cd ~/MLOps-is-all-you-need/mlops-sys/server
    docker-compose -f docker-compose-local.yml --env-file .env.local up --build
    ```
    
    ```
    # 多機模式
    cd ~/MLOps-is-all-you-need/mlops-sys/server
    docker-compose up --build
    ```

4. 完成後，可以在終端機看到包含以下紀錄，表示各項服務正常啟動
- MinIO (容器名：`minio_s3`)
    ```
    MinIO Object Storage Server
    Copyright: 2015-2023 MinIO, Inc.
    License: GNU AGPLv3 <https://www.gnu.org/licenses/agpl-3.0.html>
    Version: RELEASE.2023-12-14T18-51-57Z (go1.21.5 linux/arm64)
    Status:         1 Online, 0 Offline. 
    S3-API:http://172.19.0.2:9000 http://127.0.0.1:9090
    Console:http://172.19.0.2:9001 http://127.0.0.1:9001

    Documentation:https://min.io/docs/minto/linux/index.html
    Warning: The standard parity is set to 0. This can lead to data loss
    ```
- MLflow (容器名：`mlflow_server`)
    ```
    [2023-11-01 05:43:49 +0000] [33] [INFO] Starting gunicorn 20.1.0
    [2023-11-01 05:43:49 +0000] [33] [INFO] Listening at:http://0.0.0.0:5050(33)
    [2023-11-01 05:43:49 +0000] [33] [INFO] Using worker: sync
    [2023-11-01 05:43:49 +0000] [34] [INFO] Booting worker with pid:34
    [2023-11-01 05:43:49 +0000] [35] [INFO] Booting worker with pid:35
    [2023-11-01 05:43:49 +0000] [36] [INFO] Booting worker with pid:36
    [2023-11-01 05:43:49 +0000] [37] [INFO] Booting worker with pid:37
    ```
- Prefect (容器名：`prefect_server`)
    ```
    Successfully registered 1 block

    ┏━━━━━━━━━━━━━━━━━━━━┓
    ┃ Registered Blocks  ┃
    ┡━━━━━━━━━━━━━━━━━━━━┩
    │ Remote File System │
    └────────────────────┘

    To configure the newly registered blocks, go to the Blocks page in the Prefect 
    UI.


    ___ ___ ___ ___ ___ ___ _____ 
    | _ \ _ \ __| __| __/ __|_   _| 
    |  _/   / _|| _|| _| (__  | |  
    |_| |_|_\___|_| |___\___| |_|  

    Configure Prefect to communicate with the server with:

        prefect config set PREFECT_API_URL=http://0.0.0.0:4200/api

    View the API reference documentation at http://0.0.0.0:4200/docs

    Check out the dashboard at http://0.0.0.0:4200
    ```
- Postgres (容器名：`postgres_db`)
    ```
    PostgreSQL Database directory appears to contain a database; Skipping initialization

    2023-11-13 08:30:16.122 UTC [1] LOG:  starting PostgreSQL 15.4 (Debian 15.4-1.pgdg120+1) on x86_64-pc-linux-gnu, compiled by gcc (Debian 12.2.0-14) 12.2.0, 64-bit
    2023-11-13 08:30:16.122 UTC [1] LOG:  listening on IPv4 address "0.0.0.0", port 5432
    2023-11-13 08:30:16.122 UTC [1] LOG:  listening on IPv6 address "::", port 5432
    2023-11-13 08:30:16.270 UTC [1] LOG:  listening on Unix socket "/var/run/postgresql/.s.PGSQL.5432"
    2023-11-13 08:30:16.518 UTC [29] LOG:  database system was shut down at 2023-11-13 08:29:54 UTC
    2023-11-13 08:30:16.688 UTC [1] LOG:  database system is ready to accept connections
    ```

4. 若有看到以上的成功訊息後，接著可以透過在瀏覽器輸入對應的網址，開始使用以下 GUI 的服務

    > 瀏覽器建議使用 Google Chrome 或是 Microsoft Edge

    > 請將下方 `IP` 替換成 `localhost`(單機模式) 或是 `SERVER_IP` (多機模式)

- MinIO (網址: `http://IP:9001`，帳號：`admin`，密碼：`adminsecretkey`)

![minio_s3_success_ui](img/minio_s3_success_ui.png)
- MLflow (網址: `http://IP:5050`)

![mlflow_server_success_ui](img/mlflow_server_success_ui.png)
- Prefect (網址: `http://IP:4200`)

![prefect_server_success_ui](img/prefect_server_success_ui.png)


### 開發環境 ML Experimenter
> `多機模式` 請在 `電腦2` 執行此段落

> 請開啟新的終端機環境執行本小節的指令

1. `ml_experimenter` 包含建置開發環境需要的檔案，為確保開發環境獨立，我們先利用 conda 建立一個獨立開發環境 `mlops`，並進入該環境
    ```
    # 使用 Git Bash 的 windows 用戶需額外執行下列程式碼，才能正常使用 conda
    source activate
    ```

    ```
    conda create -n mlops python=3.10 -y    # 建立獨立開發環境
    conda activate mlops                    # 進入該開發環境
    ```
2. 下載需要的 Python 套件
    > 註：每個新的獨立環境都要重新下載一次
    ```
    cd ~/MLOps-is-all-you-need/mlops-sys/ml_experimenter
    pip install -r requirements_sys.txt
    ```
3. 建立一個專案資料夾（例如 `quick_start/`）以及在底下建立開發資料夾 `dev` ，並進入此開發資料夾。此處以 [projects/quick_start/dev](../quick_start/dev)為例
    ```
    cd ~/MLOps-is-all-you-need/projects/quick_start/dev
    ```

4. 接著設定環境變數
    - 單機模式： 將專案名稱寫進 [`mlops-sys/ml_experimenter/.env.local`](../../mlops-sys/ml_experimenter/.env.local)，並存檔
    ```
    PROJECT_NAME='my-project'  # 取消註解，並填入專案名稱
    ```

    - 多機模式：將專案名稱、 `SERVER_IP` 寫進 [`mlops-sys/ml_experimenter/.env`](../../mlops-sys/ml_experimenter/.env)，並存檔
    ```
    SERVER_IP= 'YOUR_SERVER_IP' # 取消註解，並填入 SERVER_IP
    PROJECT_NAME='my-project'  # 取消註解，並填入專案名稱
    ```

5. [Optional] 在此開發資料夾 `dev` 中，可以透過初始化 Git 與 DVC 啟用程式碼與資料版本控制服務 
    <details><summary>程式碼</summary>
    <p>

    ```
    # 單機模式
    source ~/MLOps-is-all-you-need/mlops-sys/ml_experimenter/.env.local
    git init
    dvc init
    dvc remote add -f minio_s3 ${MINIO_S3_PROJECT_BUCKET}
    dvc remote modify minio_s3 endpointurl ${MLFLOW_S3_ENDPOINT_URL}
    ```

    ```
    # 多機模式
    source ~/MLOps-is-all-you-need/mlops-sys/ml_experimenter/.env
    git init
    dvc init
    dvc remote add -f minio_s3 ${MINIO_S3_PROJECT_BUCKET}
    dvc remote modify minio_s3 endpointurl ${MLFLOW_S3_ENDPOINT_URL}
    ```
    完成後，可以在終端機看到以下結果，表示 DVC 初始化正常
    ```
    You can now commit the changes to git.

    +---------------------------------------------------------------------+
    |                                                                     |
    |        DVC has enabled anonymous aggregate usage analytics.         |
    |     Read the analytics documentation (and how to opt-out) here:     |
    |             <https://dvc.org/doc/user-guide/analytics>              |
    |                                                                     |
    +---------------------------------------------------------------------+

    What's next?
    ------------
    - Check out the documentation: <https://dvc.org/doc>
    - Get help and share ideas: <https://dvc.org/chat>
    - Star us on GitHub: <https://github.com/iterative/dvc>
    ```
    </p>
    </detail>

6. 最後我們只需要在 `.py` 中，透過加入下方程式碼導入環境變數，就能使用 MLflow 套件做模型版本控制了。
    ```
    # 單機模式
    from dotenv import load_dotenv

    load_dotenv('~/MLOps-is-all-you-need/mlops-sys/ml_experimenter/.env.local')
    ```
    
    ```
    # 多機模式
    from dotenv import load_dotenv

    load_dotenv('~/MLOps-is-all-you-need/mlops-sys/ml_experimenter/.env')
    ```
    > 程式碼範例請參考 [projects/quick_start/dev/experiment.py](../quick_start/dev/experiment.py) 

    > 更多細節說明請參考 [mnist 章節](../mnist/readme.md)

### 工作流程的排程功能 Flow Scheduler
> `多機模式` 請在 `電腦3` 執行此段落

> 請開啟新的終端機環境執行本小節的指令

1. 要幫專案建立排程，請在專案資料夾（例如 `quick_start/`）底下建立排程資料夾 `flow` ，並將開發資料夾 `dev` 的檔案複製到`flow` 中，以及將複製到 `flow` 的主要 `.py` 檔加入 Prefect 的排程功能。加入 Prefect 排程設定的方式，主要是在 Python 函式中加入 Prefect 裝飾器 (decorator)，例如：
    ```
    from prefect import flow, task

    @task()  # 設定任務
    def task1():
        pass

    @flow()  # 將任務串接成排程
    def main():
        task1()

    if __name__ == "__main__":
        main()
    ```
    > `flow` 底下務必存放 `requirements.txt` ，且其內容包含所有用到的套件，並建議附上版本

    > 設定完排程的 `.py` 請參考 [projects/quick_start/flow/prefect_flow.py](../quick_start/flow/prefect_flow.py)

    > 更多細節說明請參考 [mnist 章節](../mnist/README.md)

2. 接著我們需在 `flow` 底下建立 `config` 資料夾，並在底下存放排程設定檔 `flow.yml`。 `flow.yml` 的存放檔案結構與參數設定格式請參考 [projects/quick_start/flow/config/flow.yml](../quick_start/flow/config/flow.yml) 。

3. 在執行`工作流程的排程功能`前我們還需要設定該功能要抓取的 `flow` 路徑，以及多機模式需要設定 `SERVER_IP`
    - 單機模式：在 [mlops-sys/flow_scheduler/.env.local](../../mlops-sys/flow_scheduler/.env.local) 中加入 `flow` 路徑，然後存檔。此處以 quick_start 為例：
    ```
    FLOW_DIR = '~/MLOps-is-all-you-need/projects/quick_start/flow' # 取消註解，並設定flow 絕對路徑

    # 相對路徑寫法: 以 .env.local 位置為 root
    # FLOW_DIR = '../../projects/quick_start/flow'
    ```

    - 多機模式：在 [mlops-sys/flow_scheduler/.env](../../mlops-sys/flow_scheduler/.env) 中加入 `flow` 路徑，並加入 `SERVER_IP` ，然後存檔。此處以 quick_start 為例：
    ```
    SERVER_IP= 'YOUR_SERVER_IP' # 取消註解，並填入 SERVER_IP           
    FLOW_DIR = '~/MLOps-is-all-you-need/projects/quick_start/flow' # 取消註解，並設定flow 絕對路徑

    # FLOW_DIR 相對路徑寫法，以 .env 位置為 root
    # FLOW_DIR = '../../projects/quick_start/flow'
    ```

2.  設定完排程專案後，我們就可以透過 `工作流程的排程功能` 將專案上傳到 `Server` 的排程序列中了

    ```
    # 單機模式
    cd ~/MLOps-is-all-you-need/mlops-sys/flow_scheduler
    docker-compose -f docker-compose-local.yml --env-file .env.local up --build
    ```

    ```
    # 多機模式
    cd ~/MLOps-is-all-you-need/mlops-sys/flow_scheduler
    docker-compose up --build
    ```
2. 完成後會顯示以下紀錄，表示範例專案已經成功上傳到 Prefect 排程服務
    ```
    Work pool named 'default-agent-pool' already exists. Please try creating your work pool again with a different name.
    Found flow 'main'
    Default '.prefectignore' file written to /root/flows/.prefectignore
    Deployment YAML created at '/root/flows/main-deployment.yml'.
    Successfully uploaded 8 files to s3://prefect/main/model_training
    Deployment 'main/model_training' successfully created with id
    'b84cb77c-9a5b-4575-b603-4d95f84d0e3c'

    To execute flow runs from this deployment, start an agent that pulls work from
    the 'default-agent-pool' work pool:
    $ prefect agent start -p 'default-agent-pool'
    ```

3. 同時也可以在 Prefect 的 GUI 介面看到新加入的排程

![flow_scheduler_success_ui](img/flow_scheduler_success_ui.png)

### 工作流程的執行服務 Flow Agent
> `多機模式` 請在 `電腦4` 執行此段落

> 請開啟新的終端機環境執行本小節的指令

1. 最後，我們需要建立 `工作流程的執行服務` ，它將會負責執行上傳到 `Server` 的排程專案。 我們會先在 [`flow_agent`](../../mlops-sys/flow_agent) 資料夾底下建立每個 `執行服務` 的設定資料夾，建立方式可以根據需求複製以下範例資料夾在 [`flow_agent`](../../mlops-sys/flow_agent) 資料夾底下並改名。
    - 單機模式 - CPU版： [`default-agent-pool_ml_local_cpu`](../../mlops-sys/flow_agent/default-agent-pool_ml_local_cpu/)
    - 單機模式 - GPU版： [`default-agent-pool_ml_local_gpu`](../../mlops-sys/flow_agent/default-agent-pool_ml_local_cpu/)
    - 多機模式 - CPU版： [`default-agent-pool_ml_distributed_cpu`](../../mlops-sys/flow_agent/default-agent-pool_ml_distributed_cpu/)
    - 多機模式 - GPU版： [`default-agent-pool_ml_distributed_gpu`](../../mlops-sys/flow_agent/default-agent-pool_ml_distributed_gpu/)
    
    <details><summary>單機模式和多機模式的差異</summary>
    <p>

    兩者的差異在於多機模式透過設定 `SERVER_IP` 將 `執行服務` 與 `Server` 連線，而單機模式透過在 `docker-compose.yml` 設定 Docker Network 的方式直接將 `執行服務` 與 `Server` 連線。
    </p>
    </details>

    <details><summary>CPU 和 GPU 版本的差異</summary>
    <p>

    兩者的差異在於 GPU 版本透過在 `docker-compose.yml` 設定 resources 指定 GPU 資源，並透過 `.env` 設定 GPU ID 清單，而 CPU 版本沒有這項設定。除此之外，GPU 版本因為使用的套件之間有環境相容性的需求，所以需要在 `Dockerfile` 客製化配置環境，而 CPU 版本則可以直接使用 Prefect 提供的 Image 為基礎建立 `Dockerfile`。
    </p>
    </details>

2. 接著透過設定該資料夾底下的 `.env` 進行設定
    - `SERVER_IP`: `Server` 的IP，僅 多機模式 需要設定
    - `GPU_ID`: 要使用的 GPU ID 清單，僅 GPU版 需要設定
    - `POOL_NAME`: 執行服務歸屬的資源池
    - `QUEUE_NAME`: 負責執行的專案

3. 然後再修改該資料夾底下存放的 `requirements.txt` ，其內容需要包含執行專案排程所需的相關套件與版本

4. 最後建立執行服務
    ```
    # 單機模式 - CPU 版
    cd ~/MLOps-is-all-you-need/mlops-sys/flow_agent/default-agent-pool_ml_local_cpu
    docker-compose up --build
    ```

    ```
    # 單機模式 - GPU 版
    cd ~/MLOps-is-all-you-need/mlops-sys/flow_agent/default-agent-pool_ml_local_gpu
    docker-compose up --build
    ```

    > 多機模式需要先按照第2點設定 `SERVER_IP`

    ```
    # 多機模式 - CPU 版
    cd ~/MLOps-is-all-you-need/mlops-sys/flow_agent/default-agent-pool_ml_distributed_cpu
    docker-compose up --build
    ```

    ```
    # 多機模式 - GPU 版
    cd ~/MLOps-is-all-you-need/mlops-sys/flow_agent/default-agent-pool_ml_distributed_gpu
    docker-compose up --build
    ```


5. 完成後，會顯示以下紀錄，表示執行服務正常啟用。此服務會在任務排程時間到時，自動開始執行排程任務內容。
    ```
    Starting v2.10.9 agent connected to http://prefect_server:4200/api...

    ___ ___ ___ ___ ___ ___ _____     _   ___ ___ _  _ _____
    | _ \ _ \ __| __| __/ __|_   _|   /_\ / __| __| \| |_   _|
    |  _/   / _|| _|| _| (__  | |    / _ \ (_ | _|| .` | | |
    |_| |_|_\___|_| |___\___| |_|   /_/ \_\___|___|_|\_| |_|


    Agent started! Looking for work from work pool 'default-agent-pool'...
    ```