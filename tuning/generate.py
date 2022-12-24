#!/usr/bin/env python

import argparse
import json
import os
import pathlib
import subprocess

parser = argparse.ArgumentParser()

parser.add_argument("--test-directory", type=pathlib.Path, required=True)
parser.add_argument("--source-directory", type=pathlib.Path, required=True)


def stringify(directory: pathlib.Path) -> str:
    # Initialize an empty string to store the contents of the files
    contents = ""

    # Iterate over all the files and directories in the given directory
    for path in directory.rglob('*.py'):
        # Read the contents of the file
        with open(path) as f:
            file_contents = f.read()

        # Add a header line with the file path and the contents of the file to the overall contents string
        contents += "> {}\n{}\n".format(path, file_contents)

    return contents


def add_example(test_directory, source_directory):
    prompt = stringify(test_directory)
    completion = stringify(source_directory)
    with open("example.jsonl", "a+") as f:
        f.write(json.dumps({"prompt": prompt, "completion": completion}) + "\n")


args = parser.parse_args()
test_directory = args.test_directory
source_directory = args.source_directory

parts = source_directory.parts
for i in range(len(parts)):
    directory = pathlib.Path(parts[:len(parts) - i])
    print(directory)
    if (directory / ".git").exists():
        break
else:
    raise RuntimeError("Could not find .git directory")

original_directory = os.getcwd()

result = subprocess.run(
    ['cd', str(directory)],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
)

try:
    while test_directory.exists() and source_directory.exists():
        add_example(test_directory, source_directory)
        result = subprocess.run(
            ['git', 'checkout', 'HEAD^'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        if result.returncode != 0:
            raise Exception(result.stderr.decode())
finally:
    subprocess.run(['cd', original_directory])
