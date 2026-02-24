
import unittest
import mlflow
import os

class TestModelLoading(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
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

        # load the model from Mlflow registry
        cls.model_name = 'my_model'
        cls.model_version = cls.get_latest_model_version(cls.model_name)
        cls.model_uri = f'models:/{cls.model_name}/{cls.model_version}'
        cls.model = mlflow.pyfunc.load_model(cls.model_uri)

    @staticmethod
    def get_latest_model_version(model_name):
        client = mlflow.tracking.MlflowClient()
        latest_version = client.get_latest_versions(model_name,stages=['Staging'])
        return latest_version[0].version if latest_version else None
    
    def test_model_loaded_properly(self):
        self.assertIsNotNone(self.model)

if __name__ == '__main__':
    unittest.main()