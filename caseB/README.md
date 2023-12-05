# Case B

# Case B 模型部署案例分享

- 請先完成快速安裝
- 此案例 base on Quick Start ，主要介紹如何將訓練結果、資料前處理方式與模型上傳至 MLflow 進行紀錄，並在部署階段下載並使用。

## 功能介紹
- 自定義一個 class 用於 MLFlow 載入前處理方式與預測模型以及模型推論方法

    ```python
    # 套件宣告
    import pandas as pd
    from sklearn.preprocessing import MinMaxScaler
    from sklearn.svm import SVC
    from xgboost import XGBClassifier
    from dotenv import load_dotenv
    import mlflow
    from mlflow import MlflowClient
    import os
    from datetime import datetime
    import gdown
    ```
    1. 此 class 繼承 mlflow pythonModel
        ```python
       class TitanicPredict(mlflow.pyfunc.PythonModel):
        """Custom pyfunc class used to create customized mlflow models"""
        ...

        ```
    2. 載入前處理方式與預測模型
        - 這裡有一個 mlflow pythonModel 的內部變數 context，此變數記錄 mlflow 當中的 artifacts (artifacts 由實驗階段上傳的結果)
        - 使用 joblib 套件讀取 前處理方式 與 預測模型
        - 此 function 會在部署階段使用 mlflow.pyfunc.load_model 時觸發

        ```python
        def load_context(self, context):
        # called when mlflow.pyfunc.load_model
            import joblib
            self.preprocessor = joblib.load(context.artifacts["preprocessor"])
            self.model = joblib.load(context.artifacts["model"])

        ```
        
    3. 模型推論
        - model_input 此變數為預計要推論的資料
        - 將輸入資料進行前處理(self.preprocessor.transform)與推論(self.model.predict)
        ```python
        def predict(self, context, model_input):
            # called when model.predict 
            numerical_features = ['Age', 'SibSp', 'Parch', 'Fare']
            model_input[numerical_features] = self.preprocessor.transform(model_input[numerical_features])
            return self.model.predict(model_input)
        ```
        
    4. 評估指標
        
        ```python
        # svc 評估指標
        y_pred = model_svc.predict(X_val)
        accuracy_svc = (y_pred == y_val).sum()/y_val.shape[0]
        
        # xgb 評估指標
        y_pred = model_xgb.predict(X_val)
        accuracy_xgb = (y_pred == y_val).sum()/y_val.shape[0]
        ```
- MLflow 連線設定  
    1. MLflow 參數設定
        
        ```python
        def mlflowSet():
            # MLflow 環境設定
            load_dotenv('.env')
            os.environ["AWS_ACCESS_KEY_ID"] = os.getenv('MINIO_ROOT_USER')
            os.environ["AWS_SECRET_ACCESS_KEY"] = os.getenv('MINIO_ROOT_PASSWORD')
            os.environ["MLFLOW_S3_ENDPOINT_URL"] = os.getenv('MLFLOW_S3_ENDPOINT_URL')
            mlflow.set_tracking_uri(os.getenv('MLFLOW_TRACKING_URI'))
        ```
            
- 實驗階段
    - 大致流程與 Quick Start 相同，調整內容以下兩點：
        1. 以 joblib.dump 方式儲存前處理方式與訓練好的模型

            ```python
            joblib.dump(scaler, 'preprocessor.b')

            joblib.dump(model_svc, 'model.b')

            ```
        2. 上傳前處理模型方式與訓練好的模型
            - artifact_path : 儲存在雲端空間的路徑
            - python_model : 傳入自建的 mlflow class
            - artifacts : 儲存下來的前處理方式與訓練好的模型

            ```python
                artifacts = { 
                    # this dict will server to model as 'context.artifacts'
                    'preprocessor': 'preprocessor.b', # value = 路徑
                    'model':'model.b' # value = 路徑
                }
                mlflow.pyfunc.log_model(
                    artifact_path="Model",
                    python_model=TitanicPredict(), # 自定義 class
                    artifacts=artifacts
                )
            ```
            

# 佈署階段
    流程皆與 Quick Start 相同