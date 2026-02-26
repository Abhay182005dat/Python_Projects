import os
import pandas as pd
from flask_app.preprocessing import Flask , render_template , request
import mlflow , dagshub
from preprocessing import normalize_text
import pickle

app = Flask(__name__)

# mlflow.set_tracking_uri('https://dagshub.com/Abhay182005dat/Python_Projects.mlflow')
# dagshub.init(repo_owner='Abhay182005dat', repo_name='Python_Projects', mlflow=True)

# set up dagshub credentials for MLflow tracking
dagshub_token = os.getenv('MLOPSMINI')
if not dagshub_token:
    raise EnvironmentError("MLOPSMINI environment variable is not set")

os.environ['MLFLOW_TRACKING_USERNAME'] = dagshub_token
os.environ['MLFLOW_TRACKING_PASSWORD'] = dagshub_token

dagshub_url = 'https://dagshub.com'
repo_owner = 'Abhay182005dat'
repo_name = 'Python_Projects'

# setup mlflow tracking uri
mlflow.set_tracking_uri(f'{dagshub_url}/{repo_owner}/{repo_name}.mlflow')

app = Flask(__name__)

# load model from registry
def get_latest_model_version(model_name):
    client = mlflow.tracking.MlflowClient()
    latest_version = client.get_latest_versions(model_name, stages=['Production'])
    if not latest_version:
        latest_version = client.get_latest_versions(model_name, stages=['None'])
    return latest_version[0].version if latest_version else None

# load model from registry 
model_name = 'my_model'
model_version = 3

model_uri = f'models:/{model_name}/{model_version}'
model = mlflow.pyfunc.load_model(model_uri)

vectorizer = pickle.load(open('models/vectorizer.pkl' , 'rb'))

@app.route('/')
def home():
    return render_template('index.html' , result=None )

@app.route('/predict' , methods=['POST'])
def predict():
   
   original_text = request.form['text']

   # clean 
   cleaned_text = normalize_text(original_text)

   # apply boW
   features = vectorizer.transform([cleaned_text])

   # convert sprarse matrix to Dataframe
   features_df = pd.DataFrame.sparse.from_spmatrix(features)
   features_df = pd.DataFrame(features.toarray() , columns = [str(i) for i in range(features.shape[1])])

   # prediction
   result = model.predict(features_df)

   sentiment = int(result[0])
   sentiment_label = 'Happy' if sentiment == 1 else 'Sad'

   return render_template('index.html', prediction=sentiment_label, input_text=original_text, show_result=True)

if __name__ == '__main__':
    app.run(debug=True)