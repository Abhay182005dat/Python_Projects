import pandas as pd
import pickle
import unittest
import mlflow
import os
from sklearn.metrics import accuracy_score, recall_score , precision_score , f1_score

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
        cls.new_model_name = 'my_model'
        cls.new_model_version = cls.get_latest_model_version(cls.new_model_name)
        cls.new_model_uri = f'models:/{cls.new_model_name}/{cls.new_model_version}'
        cls.new_model = mlflow.pyfunc.load_model(cls.new_model_uri)

        # load the vectorizer
        cls.vectorizer = pickle.load(open('models/vectorizer.pkl', 'rb'))

        # load holdout test data
        cls.holdout_data = pd.read_csv('data/processed/test_bow.csv')

    @staticmethod   
    def get_latest_model_version(model_name):
        client = mlflow.tracking.MlflowClient()
        latest_version = client.get_latest_versions(model_name,stages=['Staging'])
        return latest_version[0].version if latest_version else None
    
    def test_model_loaded_properly(self):
        self.assertIsNotNone(self.new_model)

    def test_model_signature(self):
        # create a dummy input for the model based on expected input format
        input_text = 'hi how are you'
        input_data = self.vectorizer.transform([input_text])
        input_df = pd.DataFrame(input_data.toarray(), columns=[str(i) for i in range(input_data.shape[1])])

        # predict using the model to verify the inout and output shapes
        prediction = self.new_model.predict(input_df)

        # verify the input data
        self.assertEqual(input_df.shape[1] , len(self.vectorizer.get_feature_names_out()))

        # verify the output shape (assumning binary classification with a single output)
        self.assertEqual(len(prediction) , input_df.shape[0])
        self.assertEqual(len(prediction.shape) , 1)  # assume a sinle output column for binary classification

    def test_model_performance(self):
        # Extract features and labels from holdout test data
        X_holdout = self.holdout_data.iloc[:,0:-1]
        y_holdout = self.holdout_data.iloc[:,-1]

        # predict using the model 
        y_pred_new = self.new_model.predict(X_holdout)

        # Calculate performance metrics for the new model
        accuracy_new = accuracy_score(y_holdout, y_pred_new)
        precision_new = precision_score(y_holdout, y_pred_new)
        recall_new = recall_score(y_holdout, y_pred_new)
        f1_new = f1_score(y_holdout, y_pred_new)
        
        # define expected thresholds for the performance metrics
        expected_accuracy = 0.70  # Example threshold for accuracy
        expected_precision = 0.70
        expected_recall = 0.70
        expected_f1 = 0.70

        # Assert that the new model's performance meets the expected thresholds
        self.assertGreaterEqual(accuracy_new, expected_accuracy, f"Accuracy should be atleast {expected_accuracy}")
        self.assertGreaterEqual(precision_new, expected_precision, f"Precision should be atleast {expected_precision}")
        self.assertGreaterEqual(recall_new, expected_recall, f"Recall should be atleast {expected_recall}")
        self.assertGreaterEqual(f1_new, expected_f1, f"F1 Score should be atleast {expected_f1}")



if __name__ == '__main__':
    unittest.main()