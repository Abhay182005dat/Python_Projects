import logging
import json
import mlflow
from mlflow.tracking import MlflowClient
import dagshub

mlflow.set_tracking_uri('https://dagshub.com/Abhay182005dat/Python_Projects.mlflow')
dagshub.init(repo_owner='Abhay182005dat', repo_name='Python_Projects', mlflow=True)

import mlflow
print("Tracking URI:", mlflow.get_tracking_uri())
with open("reports/experiment_info.json") as f:
    data = json.load(f)

run_id = data["run_id"]

print("Run ID:", run_id)
