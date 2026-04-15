import pandas as pd
import os
import pickle

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score


BASE_DIR = os.path.dirname(__file__)

data = pd.read_csv(os.path.join(BASE_DIR, "dataset.csv"))


X_train, X_test, y_train, y_test = train_test_split(
    data["text"],
    data["label"],
    test_size=0.2,
    random_state=42
)


vectorizer = TfidfVectorizer()

X_train_vec = vectorizer.fit_transform(X_train)

X_test_vec = vectorizer.transform(X_test)


# Logistic Regression
lr = LogisticRegression()

lr.fit(X_train_vec, y_train)

lr_pred = lr.predict(X_test_vec)


# Naive Bayes
nb = MultinomialNB()

nb.fit(X_train_vec, y_train)

nb_pred = nb.predict(X_test_vec)


print("Logistic Regression accuracy:", accuracy_score(y_test, lr_pred))

print("Naive Bayes accuracy:", accuracy_score(y_test, nb_pred))


# choose best model
best_model = lr if accuracy_score(y_test, lr_pred) > accuracy_score(y_test, nb_pred) else nb


# save inside ml folder
pickle.dump(best_model, open(os.path.join(BASE_DIR, "model.pkl"), "wb"))

pickle.dump(vectorizer, open(os.path.join(BASE_DIR, "vectorizer.pkl"), "wb"))

print("Model saved successfully")