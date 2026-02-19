import logging
import json
import mlflow
from mlflow.tracking import MlflowClient
import dagshub



mlflow.set_tracking_uri('https://dagshub.com/Abhay182005dat/Python_Projects.mlflow')
dagshub.init(repo_owner='Abhay182005dat', repo_name='Python_Projects', mlflow=True)



# logging configuration
logger = logging.getLogger('model_registration')
logger.setLevel('DEBUG')

console_handler = logging.StreamHandler()
console_handler.setLevel('DEBUG')

file_handler = logging.FileHandler('model_registration_errors.log')
file_handler.setLevel('ERROR')

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

logger.addHandler(console_handler)
logger.addHandler(file_handler)

def load_model_info(file_path : str) -> dict:
    try:
        with open(file_path ,'r') as file:
            model_info = json.load(file)
        logger.debug('Model info loaded from %s' , file_path)
        return model_info
    except FileNotFoundError:
        logger.error('File not found: %s',file_path)
        raise
    except Exception as e:
        logger.error('Unexpected error occured while loading the model info: %s' , e)
        raise

def register_model(model_name : str , model_info  : dict):
    try:
        model_uri = model_info['model_uri']

        # register the model 
        model_version = mlflow.register_model(model_uri,model_name)
        logger.debug(f'Model {model_name} version {model_version.version} registered successfully.')

        # transition the model to 'staging' stage
        try:
            client = mlflow.tracking.MlflowClient()
            client.transition_model_version_stage(
                name=model_name,
                version=model_version.version,
                stage='Staging'
            )
            logger.debug(f'Model {model_name} version {model_version.version} transitioned to Staging.')
        except Exception as transition_error:
            logger.warning(f'Could not transition model to Staging stage: {transition_error}. Model is registered but not transitioned.')
    except Exception as e:
        logger.error('Error during model registration : %s' , e)
        raise

def main():
    try:
        model_info_path = './reports/experiment_info.json'
        model_info = load_model_info(model_info_path)
        model_name = 'my_model'
        register_model(model_name , model_info)
    except Exception as e:
        logger.error('Failed to complete the model registration process  : %s' , e)
        print(f'Error : {e}')

if __name__ == '__main__':
    main()