import dagshub
import mlflow

mlflow.set_tracking_uri('https://dagshub.com/Abhay182005dat/Python_Projects.mlflow')
dagshub.init(repo_owner='Abhay182005dat', repo_name='Python_Projects', mlflow=True)


with mlflow.start_run():
  mlflow.log_param('parameter name', 'value')
  mlflow.log_metric('metric name', 1)