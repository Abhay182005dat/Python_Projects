import mlflow
import dagshub
import mlflow.sklearn
from sklearn.feature_extraction.text import CountVectorizer , TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from xgboost import XGBClassifier
from sklearn.ensemble import RandomForestClassifier , GradientBoostingClassifier
from sklearn.metrics import accuracy_score , precision_score , recall_score , f1_score
import re
import string
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import numpy as np
import os
import pandas as pd


mlflow.set_tracking_uri('https://dagshub.com/Abhay182005dat/Python_Projects.mlflow')
dagshub.init(repo_owner='Abhay182005dat', repo_name='Python_Projects', mlflow=True)

df = pd.read_csv('https://raw.githubusercontent.com/campusx-official/jupyter-masterclass/main/tweet_emotions.csv').drop(columns=['tweet_id'])

# data preprocessing

def lemmatization(text):
    lemmatizer = WordNetLemmatizer()

    text = text.split()
    text = [lemmatizer.lemmatize(word) for word in text]
    return " " .join(text)

def remove_stop_words(text):
    stop_words = set(stopwords.words('english'))
    Text = [i for i in str(text).split() if i not in stop_words]
    return " ".join(Text)

def removing_numbers(text):
    text = ''.join([i for i in text if not i.isdigit()])
    return text

def lower_case(text):
    text = text.split()

    text = [y.lower() for y in text]

    return " " .join(text)

def removing_punctuations(text):
    text = re.sub('[%s]' % re.escape(string.punctuation), ' ',text)
    text = text.replace(':',"")

    # remove extra whitespaces
    text = re.sub('\s+' , ' ',text).strip()
    return text

def removing_urls(text):
    url_pattern = re.compile(r'https?://\S+|www\.\S+')
    return url_pattern.sub(r'',text)

# def remove_small_sentences(df):
#     for i in range(len(df)):
#         if len(df.text.iloc[i].split()) < 3:
#             df.text.iloc[i] = np.nan

def normalize_text(df):
    try:

        df.content = df.content.apply(lambda content : lower_case(content))
        df.content = df.content.apply(lambda content : remove_stop_words(content))
        df.content = df.content.apply(lambda content : removing_numbers(content))
        df.content = df.content.apply(lambda content : removing_punctuations(content))
        df.content = df.content.apply(lambda content : removing_urls(content))
        df.content = df.content.apply(lambda content : lemmatization(content))
        return df
    except Exception as e:
        print(f'Error during text normalization {e}')
        raise
df = normalize_text(df)

x = df['sentiment'].isin(['happiness' , 'sadness'])
df = df[x]

df['sentiment'] = df['sentiment'].replace({'sadness':0 , 'happiness':1})

mlflow.set_experiment("Bow vs Tf-idf")

vectorizers = {
    'Bow' : CountVectorizer(),
    'Tf-idf' : TfidfVectorizer()
}

# define Algorithms 
algorithms = {
    'LogisticRegression' : LogisticRegression(),
    'MultinomialNB' : MultinomialNB(),
    'XGBoost' : XGBClassifier(),
    'RandomForest' : RandomForestClassifier(),
    'GradientBoosting' : GradientBoostingClassifier()
}

# start with parent run
with mlflow.start_run(run_name='All Experiments') as parent_run:
    # Loop thorugh algorithms and feature methods (child runs)
    for algo_name , algorithm in algorithms.items():
        for vec_name , vectorizer in vectorizers.items():
            with mlflow.start_run(run_name=f'{algo_name} with {vec_name}',nested=True) as child_run:
                X = vectorizer.fit_transform(df['content'])
                y = df['sentiment']
                X_train , X_test , y_train , y_test = train_test_split(X , y , test_size=0.2 , random_state=42)

                # log processing params
                mlflow.log_param("vectorizer" , vec_name)
                mlflow.log_param("algorithm" , algo_name)
                mlflow.log_param("test_size" , 0.2)

                # Model training
                model = algorithm
                model.fit(X_train , y_train)

                # Log model params
                if algo_name == 'LogisticRegression':
                    mlflow.log_param("C" , model.C)
                elif algo_name == 'MultinomialNB' : 
                    mlflow.log_param('alpha' , model.alpha)
                elif algo_name == 'XGBoost':
                    mlflow.log_param('n_estimators' , model.n_estimators)
                    mlflow.log_param('learning_rate' , model.learning_rate)
                elif algo_name == 'RandomForest':
                    mlflow.log_param('n_estimators' , model.n_estimators)
                    mlflow.log_param('max_depth' , model.max_depth)
                elif algo_name == 'GradientBoosting':
                    mlflow.log_param('n_estimators' , model.n_estimators)
                    mlflow.log_param('learning_rate',model.learning_rate)
                    mlflow.log_param('max_depth' , model.max_depth)

                # Model evaluation
                y_pred = model.predict(X_test)
                accuracy = accuracy_score(y_test , y_pred)
                precision = precision_score(y_test , y_pred)
                recall = recall_score(y_test , y_pred)
                f1 = f1_score(y_test , y_pred)

                # log evaluation metrics
                mlflow.log_metric('accuracy' , accuracy)
                mlflow.log_metric('precision' , precision)
                mlflow.log_metric('recall' , recall)
                mlflow.log_metric('f1 score' , f1)

                # log model
                mlflow.sklearn.log_model(model , artifact_path='model')

                # save and log the notebook
                mlflow.log_artifact(__file__)

                # print the results for verification
                print(f'Algorithm : {algo_name} , Feature Engineering : {vec_name}')
                print(f'Accuracy : {accuracy}')
                print(f'Precision : {precision}')
                print(f'Recall : {recall}')
                print(f'F1 score : {f1}')
                