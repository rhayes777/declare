#!/usr/bin/env python
import argparse
import os
import subprocess
from os import environ
from pathlib import Path

import openai

openai.api_key = environ["API_KEY"]

parser = argparse.ArgumentParser()

parser.add_argument("filename", type=Path)
parser.add_argument("--prompt", default="Add code to pass the test without imports.")
parser.add_argument("-n", type=int, default=5)
parser.add_argument("--top-p", type=int, default=1)
parser.add_argument("--temperature", type=float, default=0.46, )
parser.add_argument("--max-tokens", type=int, default=626, )
parser.add_argument("--frequency-penalty", type=int, default=0, )
parser.add_argument("--presence-penalty", type=int, default=0, )

args = parser.parse_args()

filename = args.filename
prompt = args.prompt

with open(filename) as f:
    suffix = f.read()

print(f"Running declare on {filename}")

response = openai.Completion.create(
    model="code-davinci-002",
    prompt=f"# {prompt}",
    # suffix=f"\n\n{suffix}",
    temperature=args.temperature,
    max_tokens=args.max_tokens,
    n=args.n,
    top_p=args.top_p,
    frequency_penalty=args.frequency_penalty,
    presence_penalty=args.presence_penalty,
)

print("Result created. Testing.")

for n, choice in enumerate(response["choices"]):
    print(f"Testing choice {n + 1}/{args.n}")

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
        os.remove(generated_name)

print("No option worked")
exit(1)
