import os

import openai
import requests
from bs4 import BeautifulSoup
import pathlib

COMPLETIONS_MODEL = "text-davinci-003"
EMBEDDING_MODEL = "text-embedding-ada-002"

openai.api_key = os.getenv("OPENAI_API_KEY")


def get_text(url):
    response = requests.get(url)
    response.raise_for_status()
    html = response.text
    soup = BeautifulSoup(html, "html.parser")
    main = soup.find("article")
    if main is not None:
        return main.get_text()
    return "\n".join([section.get_text() for section in soup.findAll("section")[:1]])


pyproject = get_text("https://pip.pypa.io/en/stable/reference/build-system/pyproject-toml/")
setup = get_text("https://docs.python.org/3/distutils/setupscript.html")

setup_content = (pathlib.Path(__file__).parent / "setup.py").read_text()

prompt = f"""
Context: 

PyProject:

{pyproject}

Command: Convert the following setup.py to a pyproject.toml file:

{setup_content}
"""

print(openai.Completion.create(
    prompt=prompt,
    temperature=0,
    max_tokens=1000,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0,
    model=COMPLETIONS_MODEL
)["choices"][0]["text"].strip(" \n"))
