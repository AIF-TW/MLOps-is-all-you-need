# 快速安裝 - 多台電腦 + CPU 排程執行服務
此章節旨在說明如何快速安裝 MLOps 服務的各組件功能在不同電腦，並試運行各個相關服務/功能。其中， `工作流程的執行服務` 為 CPU 版本，如需 GPU 版本請參考其他章節。更多客製化安裝、套件功能介紹，請參考 `User Guide` 章節。<br>


## 系統架構
> 此章節預設圖中的電腦為不同實體電腦，讀者可以根據需求配置實體電腦的規格。

![system plot](png/sys.png)


## 事前準備
1. 請先安裝 `git` 套件 ([下載教學](https://git-scm.com/book/zh-tw/v2/%E9%96%8B%E5%A7%8B-Git-%E5%AE%89%E8%A3%9D%E6%95%99%E5%AD%B8)) 、 `docker` 套件 ([官網下載](https://www.docker.com/products/docker-desktop/)) 、 `conda` 套件 ([官網下載](https://conda.io/projects/conda/en/latest/user-guide/install/index.html#))
2. 下載此專案到所有需要部署的電腦上
```
git clone https://github.com/AIF-TW/MLOps-is-all-you-need.git
```
3. 在所有需要部署的電腦中，進入此快速安裝資資料夾
```
cd MLOps-is-all-you-need/5-Multi-computers-quick-install
```

## 檔案結構
包含 4 個服務/功能
- 伺服器 `server` -> 將部署在 `電腦1`
- 開發環境 `ml_experimenter` -> 將部署在 `電腦2`
- 工作流程的排程功能 `flow_scheduler` -> 將部署在 `電腦3`
- 工作流程的執行服務`flow_agent` -> 將部署在 `電腦4` (本章節為 CPU 版，如需 GPU 版請參考相關章節)

<details><summary>展開檔案結構圖</summary>
<p>

```
.
├── README.md
├── flow_agent
│   └── default-agent-pool_ml_cpu
│       ├── .env
│       ├── Dockerfile
│       ├── docker-compose.yml
│       ├── requirements.txt
│       └── requirements_sys.txt
├── flow_scheduler
│   ├── flow_scheduler
│   │   ├── .env
│   │   ├── Dockerfile
│   │   ├── docker-compose.yml
│   │   ├── requirements_sys.txt
│   │   └── setup.py
│   └── flows
│       └── example_flow # 範例排程專案
│           ├── data
│           │   ├── green_tripdata_2021-01.parquet
│           │   └── green_tripdata_2021-02.parquet
│           ├── flow.yaml
│           ├── prefect_flow.py
│           └── requirements.txt
├── ml_experimenter
│   ├── .env
│   └── requirements_sys.txt
└── server
    ├── .env
    ├── docker-compose.yml
    ├── init.sh
    └── prefect_setting_s3.py
```

</p>
</details>

## 開始安裝
請依序完成以下4個服務/功能的安裝。

### 伺服器 Server
> 請在 `電腦1` 執行此段落

1. 取得此電腦的 `預設電腦IP`，此 IP 將作為其他服務/功能連線到 `伺服器 Server` 的依據，本章節接下來將以 `SERVER_IP` 指稱。

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

2. 修改 `server` 資料夾中的 `.env` 檔，將上一步得到的 `SERVER_IP` 取代 `YOUR_SERVER_IP`。

3. 進入到  `server` 資料夾，並啟動伺服器服務
   ```
   cd server
   docker-compose up --build
   ```

4. 完成後，可以看到包含以下紀錄，表示各項服務正常啟動
- MinIO (容器名：`minio_s3`)
    ```
    MinIO Object Storage Server
    Copyright: 2015-2023 MinIO, Inc.
    License: GNU AGPLV3 <https://www.gnu.org/licenses/agpl-3.0.htmb
    Verston: RELEASE. 2023-10-25T06-33-25Z (go1.21.3 Linux/arm64)

    Status:         1 Online, o Offline.
    S3-API:http://172.19.0.2:9000 http://127.0.0.19090
    Console:http://172.19.0.2:9001http://127.0.0.1:9001

    Documentation:https://min.io/docs/minto/linux/index.html
    Warning: The standard parity is set to 0. This can lead to data loss
    ```
- MLflow (容器名：`mlflow_server`)
    ```
    [2023-11-01 05:43:49 +0000] [33] [INFO] Starting gunicorn 20.1.0
    [2023-11-01 05:43:49 +0000] [33] [INFO]Listening at:http://0.0.0.0:5050(33)
    [2023-11-01 05:43:49 +0000] [33] [INFO] Using worker: sync
    [2023-11-01 05:43:49 +0000] [34] [INF0]Booting worker with pid:34
    [2023-11-01 05:43:49 +0000] [35] [INFO] Booting worker with pid:35
    [2023-11-01 05:43:49 +0000] [36] [INF0] Booting worker withpid:36
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

5. 確保正常啟動後，可以透過在瀏覽器輸入對應的網址，開始使用以下 GUI 的服務
    > 註：請將 `SERVER_IP` 替換成步驟一取得的 `預設電腦IP`
- MinIO (網址: `http://SERVER_IP:9001`，帳號：`admin`，密碼：`adminsecretkey`)

![minio_s3_success_ui](png/minio_s3_success_ui.png)
- MLflow (網址: `http://SERVER_IP:5050`)

![mlflow_server_success_ui](png/mlflow_server_success_ui.png)
- Prefect (網址: `http://SERVER_IP:4200`)

![prefect_server_success_ui](png/prefect_server_success_ui.png)


### 開發環境 ML Experimenter
> 請在 `電腦2` 執行此段落
> 註：如果是 Windows作業系統，請在 Git Bash 執行 下方指令 (Git Bash 會在下載 Git 套件的時候一併下載，使用方式請參考 [如何在VScode 使用 git bash](https://code.visualstudio.com/docs/sourcecontrol/intro-to-git#_git-bash-on-windows))

1. 修改 `ml_experimenter` 資料夾中的 `.env` 檔，用 `伺服器` 段落取得的 `SERVER_IP` 取代 `<OUR_SERVER_IP`。
2. 利用 conda 建立一個獨立開發環境 `mlops`，並進入該環境
    ```
    conad create -n mlops python=3.10 -y    # 建立獨立開發環境
    conda activate mlops                    # 進入該開發環境
    ```
3. 將 `ml_experimenter` 中的檔案複製到你的開發專案資料夾，並進入該資料夾準備進行專案初始化 (此範例示範直接以 `ml_experimenter` 作為開發專案資料夾)
    ```
    cd ml_experimenter
    ```
4. 利用 conda 建立一個獨立開發環境 `mlops`，並進入該環境
    ```
    conad create -n mlops python=3.10 -y    # 建立獨立開發環境
    conda activate mlops                    # 進入該開發環境
    ```
5. 下載需要的 python 套件
    > 註：每個新的獨立環境都要重新下載一次
    ```
    pip install -r requirements_sys.txt
    ```
6. 設定環境變數
    > 註：每次使用新的終端機介面都需要重新設定環境變數。
    ```
    source .env
    ```
7. [可選擇] 初始化 DVC 資料版本控制服務 
    ```
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

8. 可以在這個資料夾開始你的專案開發了！

### 工作流程的排程功能 Flow Scheduler
> 請在 `電腦3` 執行此段落

此功能在快速安裝時，僅利用範例專案做測試。詳細使用方法請參考 `快速使用` 章節。

1. 修改 `flow_scheduler/flow_scheduler` 資料夾中的 `.env` 檔，用 `伺服器` 段落取得的 `SERVER_IP` 取代 `YOUR_SERVER_IP`。

2.  進入`工作流程的排程功能` 並啟動

    ```
    cd flow_scheduler/flow_scheduler
    docker-compose up --build
    ```
3. 完成後會顯示以下紀錄，表示範例專案已經成功上傳到 `Prefect` 排程服務
    ```
    Work pool named 'default-agent-pool' already exists. Please try creating your work pool again with a different name.
    Found flow 'main'
    Default '.prefectignore' file written to /root/flows/.prefectignore
    Deployment YAML created at '/root/flows/main-deployment.yaml'.
    Successfully uploaded 8 files to s3://prefect/main/model_training
    Deployment 'main/model_training' successfully created with id
    'b84cb77c-9a5b-4575-b603-4d95f84d0e3c'

    To execute flow runs from this deployment, start an agent that pulls work from
    the 'default-agent-pool' work pool:
    $ prefect agent start -p 'default-agent-pool'
    ```

4. 同時也可以在 `Prefect` 的 GUI 介面看到新加入的排程

![flow_scheduler_success_ui](png/flow_scheduler_success_ui.png)

### 工作流程的執行服務 Flow Agent
> 請在 `電腦4` 執行此段落

此服務在快速安裝時，僅利用範例專案做測試，測試後刪除。詳細使用方法請參考 `快速使用` 章節。

1. 修改 `flow_agent/default-agent-pool_ml_cpu` 資料夾中的 `.env` 檔，用 `伺服器` 段落取得的 `SERVER_IP` 取代 `YOUR_SERVER_IP`。

2. 進入 `工作流程的執行服務` 的 cpu 範例服務資料夾，並啟動範例服務
    ```
    cd flow_agent/default-agent-pool_ml_cpu
    docker-compose up --build
    ```

3. 完成後，會顯示以下紀錄，表示此服務正常啟用
    ```
    Starting v2.10.9 agent connected to http://prefect_server:4200/api...

    ___ ___ ___ ___ ___ ___ _____     _   ___ ___ _  _ _____
    | _ \ _ \ __| __| __/ __|_   _|   /_\ / __| __| \| |_   _|
    |  _/   / _|| _|| _| (__  | |    / _ \ (_ | _|| .` | | |
    |_| |_|_\___|_| |___\___| |_|   /_/ \_\___|___|_|\_| |_|


    Agent started! Looking for work from work pool 'cpu_pool'...
    ```

4. 最後，刪除服務
    - 先中止服務：在終端機輸入 `control + c`
    - 刪除服務：在終端機輸入
        ```
        docker-compose down 
        ```