import pandas as pd
import mlflow
from mlflow import MlflowClient
import os
from dotenv import load_dotenv

# 系統環境變數設定(單機版)
load_dotenv("../../mlops-sys/ml_experimenter/.env.local")

# 系統環境變數設定(多機版)
# load_dotenv("../../mlops-sys/ml_experimenter/.env")

def main():

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
        name="Titanic_model", version=int(mv.version), stage="Production"
    )

    # 下載註冊後的模型, 並使用MLflow 讀取模型
    model_name = "Titanic_model"
    stage = "Production"

    model = mlflow.pyfunc.load_model(model_uri=f"models:/{model_name}/{stage}")
    
    # 建立一筆測試資料，並進行預測
    test = pd.DataFrame()
    test["Age"] = [0.28]
    test["SibSp"] = [0.0]
    test["Parch"] = [0.0]
    test["Fare"] = [0.014151]

    print(test)
    result = model.predict(test)
    if result :
        print("Survived")
    else:
        print("Dead")

if __name__=="__main__":
    main()