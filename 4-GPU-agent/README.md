# 建立多GPU實驗環境
多人團隊進行協作時，如果有多個GPU的裝置，就能善用每一個GPU作為一個Agent來執行多個排程。在此範例中我們將建立適合多人使用的[Prefect Work pools](https://docs.prefect.io/2.14.3/concepts/work-pools/)，模擬當設備有雙GPU，又有2個排程要進行時可以怎麼使用Prefect。

## 實作
**注意事項：**
1. 此範例需要用到[0-Quick-Install](../0-Quick-Install/)所建立的服務
2. 如果是單GPU設備，則只需要執行GPU 0的步驟就好（例如建立「MNIST_gpu_0」排程）
3. 確認[CUDA](https://www.nvidia.com/zh-tw/geforce/technologies/cuda/)是否已設定好<details><summary>確認方式：</summary>

    在終端機輸入`nvidia-smi`來開啟[NVIDIA System Management Interface](https://developer.nvidia.com/nvidia-system-management-interface)，假如能看到所有已裝備的GPU以及CUDA版本，如下圖，就代表所需的驅動都已裝好。如果未能看到設備安裝的GPU，可能是因為沒有正確安裝驅動程式。
    ![img](./png/nvidia-smi.png)

    </details>

## 1 透過Prefect建立2個排程
將「MNIST_gpu_0」、「MNIST_gpu_1」排程分別上傳到Prefect伺服器上：
### 1.1 複製`MNIST.dvc`到工作資料夾
將`flows_mnist/data/MNIST.dvc`分別拷貝到`flow_scheduler/flows_mnist_gpu_0/data/`、`flow_scheduler/flows_mnist_gpu_1/data/`。兩個資料夾都要有`MNIST.dvc`才能從DVC remote下載資料。

### 1.2 分別建立兩個排程
#### 1.2-a 建立「MNIST_gpu_0」排程
建立Docker Compose之前請確認`flow_scheduler/flow_scheduler/.env`裡面的`FLOW_DIR`設定為「`FLOW_DIR='./flows_mnist_gpu_0'`」：
````commmandline
cd flow_scheduler/flow_scheduler/
docker compose up -d --build
````

#### 1.2-b 建立「MNIST_gpu_1」排程
此步驟跟2.1.2-a在相同的路徑下執行，但因為這兩個步驟是要建立不同排程，因此要上傳不同的`flows`資料夾。建立Docker Compose之前請先到`flow_scheduler/flow_scheduler/.env`裡面的`FLOW_DIR`更改設定為「`FLOW_DIR='./flows_mnist_gpu_1'`」：
````commmandline
docker compose up -d --build
````

## 2 分別建立兩個Prefect Agent
### 2.1 建立「gpu_pool_0」
如果是在單GPU設備，就不需要執行2.2。
````commmandline
cd flow_agent_pool_ml_gpu_0/
docker compose up -d --build
````

<details><summary>在Docker Compose指派GPU的方式</summary>

以[`flow_agent_pool_ml_gpu_0/docker-compose.yml`](./flow_agent/flow_agent_pool_ml_gpu_0/docker-compose.yml)為範例，只要在`deploy.resources.reservations`指定`device_ids`，就能以該代號的GPU執行這個Pool的任務，例如：
````yaml
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              device_ids: ["0"]  # <-- 使用id = 0的GPU
              capabilities: [gpu]
````
</details>

### 2.2 建立「gpu_pool_1」
````commmandline
cd flow_agent_pool_ml_gpu_1/
docker compose up -d --build
````

## 3 確認排程是否建立成功
前往[`http://localhost:4200/`](http://localhost:4200/)，確認剛才建立的排程是否有出現。

![img](./png/Prefect_flows.png)

> 如果還沒到排程的時間，程式就不會開始執行，我們可以用以下方式來快速執行一次：
> 1. 展開「MNIST_gpu_0」或「MNIST_gpu_1」，會看到「model_training_mnist_gpu_0」或「model_training_mnist_gpu_1」，以下截圖是展開「MNIST_gpu_1」的樣子
> 2. 點一下該卡片的右上角的「 ⋮ 」按鈕，點一下「Quick run」即可快速執行一次
> ![img](./png/Prefect_quick_run.png)

Flow Run隨即開始執行：
![img](./png/Prefect_flow_run.png)

到目前為止我們已經實際操作完CPU與GPU Agent的建立，並用來進行模型訓練，未來就能依設備與需求，自行組合出最適合團隊使用的Prefect pool。
