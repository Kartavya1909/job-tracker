import pickle
import os

from .role_extractor import extract_role
from .company_extractor import extract_company


BASE_DIR = os.path.dirname(__file__)


model = pickle.load(
    open(os.path.join(BASE_DIR, "model.pkl"), "rb")
)

vectorizer = pickle.load(
    open(os.path.join(BASE_DIR, "vectorizer.pkl"), "rb")
)


def predict_email_data(subject, body, sender):

    text = subject + " " + body

    vector = vectorizer.transform([text])

    status = model.predict(vector)[0]

    role = extract_role(text)

    company = extract_company(subject, sender)

    return status, role, company