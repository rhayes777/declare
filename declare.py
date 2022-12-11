from os import environ
from pathlib import Path
from sys import argv

import openai
import pytest as pytest

openai.api_key = environ["API_KEY"]
filename = Path(argv[1])

with open(filename) as f:
    suffix = f.read()


response = openai.Completion.create(
    model="code-davinci-002",
    prompt="# Add code to pass the test without imports",
    suffix=f"\n\n{suffix}",
    temperature=0.9,
    max_tokens=512,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0
)

result = response["choices"][0]["text"]

generated_name = filename.with_name(f"{filename.stem}_generated.py")

with open(generated_name, "w+") as f:
    f.write(f"{result}\n\n{suffix}")


pytest.main([str(generated_name)])
