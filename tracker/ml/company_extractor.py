import re


COMMON_COMPANIES = [

    "google",

    "microsoft",

    "amazon",

    "infosys",

    "tcs",

    "wipro",

    "accenture",

    "cognizant",

    "capgemini",

]


def extract_company(subject, sender):

    text = (subject + " " + sender).lower()

    for c in COMMON_COMPANIES:

        if c in text:

            return c.capitalize()


    match = re.search(r'@([\w\.-]+)', sender)

    if match:

        domain = match.group(1)

        return domain.split(".")[0].capitalize()

    return "Unknown"