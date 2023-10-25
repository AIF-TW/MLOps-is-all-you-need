# Quick start

# 開發實驗階段

- 請先完成快速安裝
- 此為開發實驗階段主要跟大家分享如何將過程紀錄在MLflow中，並將每次的實驗紀錄(模型參數, Loss曲線, 評估指標…等)儲存起來，方便之後多實驗結果比較。

## 功能介紹

- 紀錄模型超參數及訓練結果、並將模型存到 Minio裡面
    ```python
    import pandas as pd
    from sklearn.preprocessing import MinMaxScaler, OneHotEncoder
    from sklearn.model_selection import train_test_split
    from sklearn.svm import SVC
    from xgboost import XGBClassifier
    from dotenv import load_dotenv
    import mlflow
    from mlflow import MlflowClient
    import os
    from datetime import datetime
    ```
    1. 從 DVC 獲取資料
        
        
    2. 資料前處理
        
        ```python
        # 將 Age 的缺失值補 Age 的平均數
        data['Age'].fillna(data['Age'].mean(), inplace = True) # inplace=True 表示覆蓋掉原資料
        
        # 將 Embarked 的缺失值補 Embarked 的眾數
        data['Embarked'].fillna(data['Embarked'].mode()[0], inplace = True)
        
        # 將 Fare 的缺失值補 Fare 的中位數
        data['Fare'].fillna(data['Fare'].median(), inplace = True)
        
        # drop 較為不重要的欄位
        drop_column = ['PassengerId','Cabin', 'Ticket', 'Name']
        data.drop(drop_column, axis=1, inplace = True)
        
        # 資料切分，並紀錄random_state
        random_state = 311
        test_size = 0.2
        data_train, data_val = train_test_split(data,
                                                test_size=test_size,
                                                shuffle=True, 
                                                random_state=random_state)
        # 資料 Ground Truth 設定
        y_train = data_train.Survived
        X_train = data_train.drop(columns='Survived')
        
        y_val = data_train.Survived
        X_val = data_train.drop(columns='Survived')
        
        # 類別變項與連續變項正規化
        categorical_features = ['Pclass', 'Sex', 'Embarked']
        numerical_features = ['Age', 'SibSp', 'Parch', 'Fare']
        X_train.Pclass = X_train.Pclass.astype('object')
        X_val.Pclass = X_val.Pclass.astype('object')
        
        # 將類別變項進行one-hot編碼(OneHotEncoder)並紀錄到新表格
        encoder = OneHotEncoder(handle_unknown='ignore', sparse=False)
        
        X_train_onehot = pd.DataFrame(encoder.fit_transform(X_train[categorical_features]), # 將類別變項進行轉換
                                      columns=encoder.get_feature_names_out(categorical_features), # 輸入新的欄位名稱
                                      index=X_train.index) # 紀錄資料順序
                                      
        X_val_onehot = pd.DataFrame(encoder.transform(X_val[categorical_features]), # 將類別變項進行轉換
                                    columns=encoder.get_feature_names_out(categorical_features), # 輸入新的欄位名稱
                                    index=X_val.index) # 紀錄資料順序
        
        # 將連續變項歸一化(MinMaxScaler): 將數值壓縮到0~1之間
        scaler = MinMaxScaler()
        
        X_train[numerical_features] = scaler.fit_transform(X_train[numerical_features])
        X_val[numerical_features] = scaler.transform(X_val[numerical_features])
        
        # 合併(concat)處理後的類別變項欄位、連續變項欄位
        X_train = pd.concat([X_train_onehot, X_train[numerical_features]], axis=1)
        X_val = pd.concat([X_val_onehot, X_val[numerical_features]], axis=1)
        ```
        
    3. 模型設計
        
        ```python
        # 建立模型
        model_svc = SVC(C=1.0,        # Regularization parameter
                        kernel='rbf') # kernel
        
        model_xgb = XGBClassifier(max_depth=2,
                                  learning_rate=0.1)
        
        # 訓練模型
        model_svc.fit(X_train, y_train)
        
        model_xgb.fit(X_train, y_train,
                      eval_set=[(X_val, y_val)])
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
        
    5. 實驗紀錄至MLflow
        - MLflow 參數設定
            
            ```python
            load_dotenv('.env')
            os.environ["AWS_ACCESS_KEY_ID"] = os.getenv('MINIO_ROOT_USER')
            os.environ["AWS_SECRET_ACCESS_KEY"] = os.getenv('MINIO_ROOT_PASSWORD')
            os.environ["MLFLOW_S3_ENDPOINT_URL"] = os.getenv('MLFLOW_S3_ENDPOINT_URL')
            
            mlflow.set_tracking_uri(os.getenv('MLFLOW_TRACKING_URI'))
            
            experiment_name = 'Titanic'
            existing_exp = mlflow.get_experiment_by_name(experiment_name)
            
            if not existing_exp:
                mlflow.create_experiment(experiment_name, "s3://mlflow/")
            
            mlflow.set_experiment(experiment_name)
            ```
            
        - 實驗紀錄
            
            ```python
            # XGBoost 實驗紀錄
            now = datetime.now()
            dt_string = now.strftime("%Y-%m-%d %H-%M-%S")
            with mlflow.start_run(run_name='Run_%s' % dt_string):
                mlflow.set_experiment_tag('developer', 'GU')
            
                mlflow.log_params({
                    'Model': "XGboost",
                    'Learning rate': 0.1,
                })
                mlflow.log_metric("Test Accuracy", accuracy_xgb)
                mlflow.xgboost.log_model(model_xgb, artifact_path='Model')
            
            # SVC 實驗紀錄
            now = datetime.now()
            dt_string = now.strftime("%Y-%m-%d %H-%M-%S")
            with mlflow.start_run(run_name='Run_%s' % dt_string):
                mlflow.set_experiment_tag('developer', 'GU')
            
                mlflow.log_params({
                    'Model': 'SVC',
                    'C': 1,
                    'kernel':'rbf'
                })
                mlflow.log_metric("Test Accuracy", accuracy_svc)
                mlflow.sklearn.log_model(model_svc, artifact_path='Model')
            ```
            

# 佈署階段

- 請先完成快速安裝與開發實驗階段
- 此部署階段主要跟大家分享如何將訓練好的模型進行部署，一般來說會有兩道手續：
    1. 從眾多實驗中找出要將哪個模型進行部署，需要對該模型進行"註冊"(Register)
    2. 使用註冊後的進行部署，並實際進行資料推論
    - 因為部署階段需要使用到前面安裝步驟的相關套件，所以請先確保有確實完成快速安裝
    - 此階段需要幾個訓練完成的模型並上傳至 MLflow，也請確定"開發實驗階段"有確實完成
    
    ## **功能介紹**
    
    1. 註冊模型(Register model)
        
        ```python
        import mlflow
        from mlflow import MlflowClient
        ```
        
        - 獲得實驗編號
            
            ```python
            target_experiments = {}
            for rm in mlflow.search_experiments(filter_string="name = 'Titanic'"):
                target_experiments = dict(rm)
            
            experiment_id = target_experiments['experiment_id']
            ```
            
        - 透過實驗編號取得每一次的模型紀錄
            
            ```python
            runs_df = mlflow.search_runs(experiment_ids=experiment_id)
            runs_df = runs_df.sort_values(by=['metrics.Test Accuracy'], ascending=False)
            runs_df.reset_index(inplace=True)
            ```
            
        - 將評估指標表現最好的模型進行”註冊“
            
            ```python
            best_run = runs_df.iloc[0]
            best_run_id = best_run["run_id"]
            mv = mlflow.register_model(model_uri="runs:/%s/Model"%best_run_id, 
                                       name="Titanic_model")
            ```
            
        - 將註冊後的模型加入版本號(Staging, Production, Archived)
            
            ```python
            client = MlflowClient(tracking_uri=os.getenv('MLFLOW_TRACKING_URI'))
            client.transition_model_version_stage(
                name="Titanic_model", version=int(mv.version), stage="Production"
            )
            ```
            
1. 模型部署預測

```python
import mlflow.pyfunc
import numpy as np
```

- 下載註冊後的模型, 並使用MLflow 讀取模型
    
    ```python
    model_name = "Titanic_model"
    stage = "Production"
    
    model = mlflow.pyfunc.load_model(model_uri=f"models:/{model_name}/{stage}")
    ```
    
- 建立一筆測試資料，並進行預測
    
    ```python
    result = model.predict(X_val[:1])
    print(result)
    ```