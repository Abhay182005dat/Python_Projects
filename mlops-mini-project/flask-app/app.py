from flask import Flask , render_template , request
import mlflow , dagshub
from preprocessing import normalize_text
import pickle

app = Flask(__name__)

mlflow.set_tracking_uri('https://dagshub.com/Abhay182005dat/Python_Projects.mlflow')
dagshub.init(repo_owner='Abhay182005dat', repo_name='Python_Projects', mlflow=True)


# load model from registry 
model_name = 'my_model'
model_version = 3

model_uri = f'models:/{model_name}/{model_version}'
model = mlflow.pyfunc.load_model(model_uri)

vectorizer = pickle.load(open('models/vectorizer.pkl' , 'rb'))

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict' , methods=['POST'])
def predict():
   original_text = request.form['text']
   # load model from model registry

   # clean 
   cleaned_text = normalize_text(original_text)
   # apply boW
   features = vectorizer.transform([cleaned_text])

   # prediction
   result = model.predict(features)
   sentiment = int(result[0])
   sentiment_label = 'Happy' if sentiment == 1 else 'Sad'

   return render_template('index.html', prediction=sentiment_label, input_text=original_text, show_result=True)

app.run(debug=True)