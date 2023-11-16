import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.svm import SVC
from dotenv import load_dotenv
import mlflow
from mlflow import MlflowClient
import os
from datetime import datetime
import gdown
import joblib


class TitanicPredict(mlflow.pyfunc.PythonModel):
    """Custom pyfunc class used to create customized mlflow models"""
    def load_context(self, context):
        # called when mlflow.pyfunc.load_model
        import joblib
        self.preprocessor = joblib.load(context.artifacts["preprocessor"])
        self.model = joblib.load(context.artifacts["model"])

    def predict(self, context, model_input):
        # called when model.predict 
        numerical_features = ['Age', 'SibSp', 'Parch', 'Fare']
        model_input[numerical_features] = self.preprocessor.transform(model_input[numerical_features])
        return self.model.predict(model_input)
    

def mlflowSet():
    # MLflow 環境設定
    load_dotenv('.env')
    os.environ["AWS_ACCESS_KEY_ID"] = os.getenv('MINIO_ROOT_USER')
    os.environ["AWS_SECRET_ACCESS_KEY"] = os.getenv('MINIO_ROOT_PASSWORD')
    os.environ["MLFLOW_S3_ENDPOINT_URL"] = os.getenv('MLFLOW_S3_ENDPOINT_URL')
    mlflow.set_tracking_uri(os.getenv('MLFLOW_TRACKING_URI'))

def experiment():
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
    X_train[numerical_features] = scaler.fit_transform(X_train[numerical_features])
    
    joblib.dump(scaler, 'preprocessor.b')

    # 建立模型
    model_svc = SVC(C=1.0,        # Regularization parameter
                    kernel='rbf') # kernel
    
    # 訓練模型
    model_svc.fit(X_train, y_train)

    # 評估指標
    y_pred = model_svc.predict(X_train)
    accuracy_svc = (y_pred == y_train).sum()/y_train.shape[0]
    
    # MLflow 實驗名稱設定
    experiment_name = 'Titanic'
    existing_exp = mlflow.get_experiment_by_name(experiment_name)

    if not existing_exp:
        mlflow.create_experiment(experiment_name, "s3://mlflow/")
    mlflow.set_experiment(experiment_name)

    # MLflow 上面訓練結果紀錄
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

        # 上傳前處理模型與訓練好的模型
        artifacts = { # this dict will server to model as 'context.artifacts'
            'preprocessor': 'preprocessor.b', # value = 路徑
            'model':'model.b' # value = 路徑
        }
        
        with open('model.b', 'wb+') as f: 
            joblib.dump(model_svc, f)

        mlflow.pyfunc.log_model(
            artifact_path="Model",
            python_model=TitanicPredict(), # 自定義 class
            artifacts=artifacts
        )
        

def deployment():
    # 獲得實驗編號
    target_experiments = {}
    for rm in mlflow.search_experiments(filter_string="name = 'Titanic'"):
        target_experiments = dict(rm)

    experiment_id = target_experiments['experiment_id']

    # 透過實驗編號取得每一次的模型紀錄
    runs_df = mlflow.search_runs(experiment_ids=experiment_id)
    runs_df = runs_df.sort_values(by=['metrics.Test Accuracy'], ascending=False)
    runs_df.reset_index(inplace=True)

    # 將評估指標表現最好的模型進行”註冊“
    best_run = runs_df.iloc[0]
    best_run_id = best_run["run_id"]
    mv = mlflow.register_model(model_uri="runs:/%s/Model"%best_run_id, 
                            name="Titanic_model")
    
    # 將註冊後的模型加入版本號(Staging, Production, Archived)
    client = MlflowClient(tracking_uri=os.getenv('MLFLOW_TRACKING_URI'))
    client.transition_model_version_stage(
        name="Titanic_model", version=int(mv.version), stage="Staging"
    )

    # 下載註冊後的模型, 並使用MLflow 讀取模型
    model_name = "Titanic_model"
    stage = "Staging"

    model = mlflow.pyfunc.load_model(f"models:/{model_name}/{stage}")

    test = pd.DataFrame()
    test["Age"] = [40]
    test["SibSp"] = [3]
    test["Parch"] = [0.0]
    test["Fare"] = [7.5]

    if model.predict(test)[0]:
        print("Survived")
    else:
        print("Dead")

def main():
    mlflowSet()
    experiment()
    deployment()



if __name__=="__main__":
    main()