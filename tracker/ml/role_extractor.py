import re

ROLES = [

    "software engineer",

    "sde",

    "backend developer",

    "frontend developer",

    "data analyst",

    "data scientist",

    "ml engineer",

    "ai engineer",

    "intern",

    "python developer",

    "java developer",

    "full stack developer",

    "web developer",

]


def extract_role(text):

    text = text.lower()

    for role in ROLES:

        if role in text:

            return role

    return "Not specified"