import mlflow
import dagshub
import mlflow.sklearn
from sklearn.feature_extraction.text import CountVectorizer , TfidfVectorizer
from sklearn.model_selection import train_test_split , GridSearchCV
from sklearn.linear_model import LogisticRegression
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

vectorizer = CountVectorizer()
X = vectorizer.fit_transform(df['content'])
y = df['sentiment']
X_train , X_test , y_train , y_test = train_test_split(X , y , test_size=0.2 , random_state=42)


mlflow.set_experiment("Lor Hyperparameter tuning")


# define param grid 
param_grid = {
    'C' : [0.1 , 1 , 10],
    'penalty' : ['l1' , 'l2'],
    'solver' : ['liblinear'],
}

# start the parent run for hyperparameter tuning
with mlflow.start_run():

    # perform grif search
    grid_search = GridSearchCV(LogisticRegression() , param_grid=param_grid , cv = 5 , scoring='f1' , n_jobs = -1)
    grid_search.fit(X_train , y_train)

    # log each param combination as a chld run
    for params , mean_score , std_score in zip(grid_search.cv_results_['params'] , grid_search.cv_results_['mean_test_score'] , grid_search.cv_results_['std_test_score']):
        with mlflow.start_run(run_name=f'LR with params : {params}' , nested=True):
            model = LogisticRegression(**params)
            model.fit(X_train , y_train)

            # Model evaluating
            y_pred = model.predict(X_test)
            accuracy = accuracy_score(y_test , y_pred)
            precision = precision_score(y_test , y_pred)
            recall = recall_score(y_test, y_pred)
            f1 = f1_score(y_test , y_pred)

            # log params
            mlflow.log_params(params)
            mlflow.log_metric('mean_cv_score' , mean_score)
            mlflow.log_metric('std_cv_score' , std_score)
            mlflow.log_metric('accuracy' , accuracy)
            mlflow.log_metric('precision' , precision)
            mlflow.log_metric('recall' , recall)
            mlflow.log_metric('f1 score' , f1)

            # print the results for verification
            print(f'Mean CV Score : {mean_score} , Std CV score , {std_score}')
            print(f'Accuracy : {accuracy}')
            print(f'Precision : {precision}')
            print(f'Recall : {recall}')
            print(f'F1 score : {f1}')
    
    # log the best run details in the parent run
    best_params = grid_search.best_params_
    best_score = grid_search.best_score_
    mlflow.log_params(best_params)
    mlflow.log_metric('best_f1_score' , best_score)

    print(f'best Params : {best_params}')
    print(f'best F1 scores : {best_score}')

    # save and log the notebook
    mlflow.log_artifact(__file__)