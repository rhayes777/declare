from os import environ
from pathlib import Path
from sys import argv

import openai

openai.api_key = environ["API_KEY"]
filename = Path(argv[1])

with open(filename) as f:
    suffix = f.read()

result = openai.Completion.create(
    model='code-davinci-002',
    temperature=0.99,
    maximum_length=256,
    prompt="Add code to pass the tests without imports",
    suffix=suffix,
)

print(result)
