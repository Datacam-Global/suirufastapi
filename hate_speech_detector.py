#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import numpy as np
import re
from collections import Counter
from nltk.tokenize import TweetTokenizer
from nltk.corpus import stopwords
from string import punctuation
from sklearn.model_selection import train_test_split, GridSearchCV, StratifiedKFold
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
import joblib

# Load dataset
tweets = pd.read_csv('TwitterHate.csv')

# Preprocessing
tweet_list = tweets.tweet.values
lower_tweets = [twt.lower() for twt in tweet_list]
no_user = [re.sub(r"@\w+","", twt) for twt in lower_tweets]
no_url = [re.sub(r"\w+://\S+","", twt) for twt in no_user]

token = TweetTokenizer()
final_token = [token.tokenize(sent) for sent in no_url]

stop_nltk = stopwords.words("english")
stop_punct = list(punctuation)
stop_punct.extend(['...','``',"''",".."])
stop_context = ['rt', 'amp']
stop_final = stop_nltk + stop_punct + stop_context

def Remover(sent):
    return [re.sub("#","",term) for term in sent if ((term not in stop_final) & (len(term)>1))]

clean_tweets = [Remover(tweet) for tweet in final_token]
clean_tweets = [" ".join(tweet) for tweet in clean_tweets]

# Split data
x = clean_tweets
y = tweets.label.values
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.30, random_state=1)

# TFIDF Vectorization
vector = TfidfVectorizer(max_features=5000)
x_train_bow = vector.fit_transform(x_train)
x_test_bow = vector.transform(x_test)

# Logistic Regression with class balancing
logger = LogisticRegression(class_weight="balanced")
logger.fit(x_train_bow, y_train)
y_train_pred = logger.predict(x_train_bow)
y_test_pred = logger.predict(x_test_bow)

print("Initial Model Performance:")
print(classification_report(y_test, y_test_pred))

# Hyperparameter tuning
param_grid = {
    'C': [0.01, 0.1, 1, 10, 100],
    'penalty': ["l1", "l2"],
    'solver': ['liblinear']  # 'liblinear' supports both l1 and l2
}
logger3 = LogisticRegression(class_weight="balanced")
grid_search = GridSearchCV(
    estimator=logger3,
    param_grid=param_grid,
    cv=StratifiedKFold(4),
    n_jobs=-1,
    verbose=1,
    scoring="recall"
)
grid_search.fit(x_train_bow, y_train)

print("Best Parameters:", grid_search.best_params_)

# Final evaluation
y_test_pred = grid_search.best_estimator_.predict(x_test_bow)
y_train_pred = grid_search.best_estimator_.predict(x_train_bow)
print("Tuned Model Performance:")
print(classification_report(y_test, y_test_pred))

# Save model and vectorizer
joblib.dump(grid_search.best_estimator_, "twitter_hate_model.joblib")
joblib.dump(vector, "twitter_hate_vectorizer.joblib")

