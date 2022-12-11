#!/usr/bin/env python

import subprocess
import sys
from os import environ
from pathlib import Path

import openai

N_CHOICES = 20

openai.api_key = environ["API_KEY"]
filename = Path(sys.argv[1])

with open(filename) as f:
    suffix = f.read()

response = openai.Completion.create(
    model="code-davinci-002",
    prompt="# Add code to pass the test without imports",
    suffix=f"\n\n{suffix}",
    temperature=0.85,
    max_tokens=256,
    n=N_CHOICES,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0
)

print("Result created. Testing.")

for n, choice in enumerate(response["choices"]):
    print(f"Testing choice {n + 1}/{N_CHOICES}")

    text = choice["text"]
    print(text)

    generated_name = filename.with_name(f"{filename.stem}_generated.py")

    with open(generated_name, "w+") as f:
        f.write(f"{text}\n\n{suffix}")

    process = subprocess.Popen(
        ["pytest", str(generated_name)],
        stdout=subprocess.PIPE
    )
    process.wait()

    if process.returncode == 0:
        print(f"Success! Generated code is at {generated_name}")
        exit(0)
    else:
        print("Tests did not pass")

print("No option worked")
exit(1)
