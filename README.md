本專案提供wiki頁面查詢，歡迎移至[wiki頁面](https://github.com/AIF-TW/MLOps-is-all-you-need/wiki/home)方便觀看。

# 簡介
此專案由AIF([財團法人人工智慧科技基金會](https://aif.tw/))維護製作，希望透過結合市面上各個優秀的MLOps開源軟體的優點，讓使用者可以更快速親民的接觸MLOps的世界。

# 特色
目前市面上 MLOps 有非常多已開發軟體可以選用，在眾多百花撩亂的產品中，我們挑選了優秀的幾個項目，並重新整合後讓使用者們可以更快速上手，且更能發揮到每個產品的優點。
這些環境在此專案都使用 Docker 建置，方便使用者快速建立環境且跨平台使用，省去建立環境時除錯的麻煩。

我們將幾個優秀的工具結合在一起且取其優點，例如 MLFlow、DVC、Prefect 及 MinIO，如果您有興趣瞭解為什麼挑這幾個項目可以至 [<由開發團隊的需求出發，從無到有設計一個實用的 MLOps 系統>](https://edge.aif.tw/design-mlops-system) 閱讀更多資訊。

# 可以做到什麼
此專案涵蓋了您所想的到所有市面上大多數的 MLOps 功能，包含**自動工作排程**、**資料與模型的版本控制**、**儲存每次的訓練結果及超參數組合**等，您也可以至範例章節下手，選擇自己會需要的功能做閱讀使用，若對 MLOps 有興趣也可以至 [<AI 專案開發一定要用 MLOps 嗎？從專案流程看起>](https://edge.aif.tw/about-mlops-project-flow) 查閱更多內容。

# 建議閱讀順序
請您先至[0-Quick-install](https://github.com/AIF-TW/MLOps-is-all-you-need/wiki/0%E2%80%90Quick%E2%80%90install)章節進行環境安裝

接著可以從 [1-Quick-start](https://github.com/AIF-TW/MLOps-is-all-you-need/wiki/1%E2%80%90Quick%E2%80%90start)章節進行閱讀，了解整個系統大致上可以做到的功能。

接著可以按照順序逐一往下閱讀，或是有某項功能立即性的需求，也可以跳著閱讀。

- [2-Model-deploy](https://github.com/AIF-TW/MLOps-is-all-you-need/wiki/2%E2%80%90Model%E2%80%90deploy)

  利用MLFlow載入**前處理方式**及**模型推論方法**

- [3-MNIST-example](https://github.com/AIF-TW/MLOps-is-all-you-need/wiki/3%E2%80%90MNIST%E2%80%90example)

  此篇教學內容比較多，有以下
    1. 透過DVC進行資料版本控制
    2. 使用MLflow追蹤模型訓練結果
    3. 透過Prefect對模型再訓練進行自動化的排程

- [4-GPU-agent](https://github.com/AIF-TW/MLOps-is-all-you-need/wiki/4%E2%80%90GPU%E2%80%90agent)

  建立多GPU實驗環境

- [5-Multi-computers-quick-install](https://github.com/AIF-TW/MLOps-is-all-you-need/wiki/5%E2%80%90Multi%E2%80%90computers%E2%80%90quick%E2%80%90install)

  建立多台電腦/伺服器的環境

