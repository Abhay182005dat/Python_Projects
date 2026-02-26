import os 
import mlflow

def promote_model():
    # set up dagshub credentials for mlflow tracking
    dagshub_token = os.getenv("MLOPSMINI")
    if not dagshub_token:
        raise EnvironmentError("MLOPSMINI environment variable is not set")
    
    os.environ['MLFLOW_TRACKING_USERNAME'] = dagshub_token
    os.environ['MLFLOW_TRACKING_PASSWORD'] = dagshub_token

    dagshub_url = 'https://dagshub.com'
    repo_owner = 'Abhay182005dat'
    repo_name = 'Python_Projects'

    # setup mlflow tracking uri
    mlflow.set_tracking_uri(f'{dagshub_url}/{repo_owner}/{repo_name}.mlflow')

    client = mlflow.tracking.MlflowClient()

    model_name = 'my_model'
    # get the latest model version in staging
    latest_version_staging = client.get_latest_versions(model_name, stages=['Staging'])[0].version

    # archive the current production model if exists
    prod_versions = client.get_latest_versions(model_name, stages=['Production'])
    for version in prod_versions:
        client.transition_model_version_stage(
            name=model_name,
            version=version.version,
            stage='Archived'
        )
    # promote the staging model to production
    client.transition_model_version_stage(
        name=model_name,
        version=latest_version_staging,
        stage='Production'
    )
    print(f"Model version {latest_version_staging} promoted to Production stage.")

if __name__ == '__main__':
    promote_model()
