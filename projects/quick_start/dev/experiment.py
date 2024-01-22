import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.svm import SVC
from xgboost import XGBClassifier
import mlflow
import os
from datetime import datetime
import gdown
from dotenv import load_dotenv

# 系統環境變數設定(單機版)
load_dotenv("../../../mlops-sys/ml_experimenter/.env.local")

# 系統環境變數設定(多機版)
# load_dotenv("../../../mlops-sys/ml_experimenter/.env")

def main():

    # 使用 Gdown 獲取資料
    # 資料下載 url
    if not os.path.exists('data'):
        os.mkdir('data')

    url = "https://drive.google.com/file/d/13_yil-3-ihA_px4nFdWq8KVoQWxxffHm/view?usp=sharing"
    gdown.download(url, output='data/titanic_data.csv', quiet=False, fuzzy=True)

    # 資料讀取
    data = pd.read_csv("data/titanic_data.csv")

    # 將 Age 的缺失值補 Age 的平均數
    data['Age'].fillna(data['Age'].mean(), inplace = True)
    # 資料 Ground Truth 設定
    y_train = data.Survived
    X_train = data.drop(columns='Survived')
    numerical_features = ['Age', 'SibSp', 'Parch', 'Fare']
    X_train = X_train[numerical_features]

    # 將連續變項歸一化(MinMaxScaler): 將數值壓縮到0~1之間
    scaler = MinMaxScaler()
    X_train = scaler.fit_transform(X_train)
    
    # 建立模型
    model_svc = SVC(C=1.0,        
                    kernel='rbf')

    model_xgb = XGBClassifier(max_depth=2,
                            learning_rate=0.1)
    
    # 訓練模型
    model_svc.fit(X_train, y_train)
    model_xgb.fit(X_train, y_train)

    # 評估指標
    y_pred = model_svc.predict(X_train)
    accuracy_svc = (y_pred == y_train).sum()/y_train.shape[0]

    y_pred = model_xgb.predict(X_train)
    accuracy_xgb = (y_pred == y_train).sum()/y_train.shape[0]

    # MLflow 實驗名稱設定
    experiment_name = 'Titanic'
    existing_exp = mlflow.get_experiment_by_name(experiment_name)

    if not existing_exp:
        mlflow.create_experiment(experiment_name, "s3://mlflow/")
    mlflow.set_experiment(experiment_name)

    # XGBoost 實驗紀錄
    now = datetime.now()
    dt_string = now.strftime("%Y-%m-%d %H-%M-%S")
    with mlflow.start_run(run_name='Run_%s' % dt_string):
        # 設定開發者名稱
        mlflow.set_experiment_tag('developer', 'aif')

        # 設定需要被紀錄的參數
        mlflow.log_params({
            'Model': "XGboost",
            'Learning rate': 0.1,
        })

        # 設定需要被紀錄的評估指標
        mlflow.log_metric("Test Accuracy", accuracy_xgb)

        # 上傳訓練好的模型
        mlflow.xgboost.log_model(model_xgb, artifact_path='Model')

    # SVC 實驗紀錄
    now = datetime.now()
    dt_string = now.strftime("%Y-%m-%d %H-%M-%S")
    with mlflow.start_run(run_name='Run_%s' % dt_string):
        # 設定開發者名稱
        mlflow.set_experiment_tag('developer', 'GU')

        # 設定需要被紀錄的參數
        mlflow.log_params({
            'Model': 'SVC',
            'C': 1,
            'kernel':'rbf',
        })

        # 設定需要被紀錄的評估指標
        mlflow.log_metric("Test Accuracy", accuracy_svc)
        # 上傳訓練好的模型
        mlflow.sklearn.log_model(model_svc, artifact_path='Model')

if __name__=="__main__":
    main()