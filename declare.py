#!/usr/bin/env python

from os import environ
from pathlib import Path
from sys import argv
from time import sleep

import openai
import pytest as pytest

N_ATTEMPTS = 5

openai.api_key = environ["API_KEY"]
filename = Path(argv[1])

with open(filename) as f:
    suffix = f.read()


for attempt in range(N_ATTEMPTS):
    print(f"Attempt {attempt + 1}/{N_ATTEMPTS}...")
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
    print("Result created. Testing.")

    generated_name = filename.with_name(f"{filename.stem}_generated.py")

    with open(generated_name, "w+") as f:
        f.write(f"{result}\n\n{suffix}")

    sleep(1)

    code = pytest.main([str(generated_name)])

    if code == 0:
        print(f"Success! Generated code is at {generated_name}")
        break
    else:
        print("Tests did not pass")
