#!/usr/bin/env python

import argparse
import importlib
import json
import pathlib
import subprocess
import sys

import coverage
import pytest

parser = argparse.ArgumentParser()

parser.add_argument("--test", type=pathlib.Path, required=True)
parser.add_argument("--source", type=pathlib.Path, required=True)


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
test_directory = args.test
source_directory = args.source

sys.path.append(str(source_directory.parent))

for path in test_directory.rglob('test_*.py'):
    for test_function in [f for f in dir(importlib.import_module(".".join(path.with_suffix("").parts))) if
                          f.startswith("test_")]:
        # Run the tests with the `--cov` option to collect coverage data
        result = pytest.main([str(path), "-k", test_function, f"--cov={source_directory}"])

        # Check the exit code of the test run
        if result == 0:
            print(f"Test run for {path}.{test_function} was successful")

            files = coverage.data.CoverageData().measured_files()

            cov = coverage.Coverage()
            cov.load()
            data = cov.get_data()
            for file in data.measured_files():
                line_numbers = data.lines(file)
                if len(line_numbers) == 0:
                    print(f"File {file} was not covered")
                    continue

                covered_lines = []
                with open(file) as f:
                    lines = f.readlines()
                    for line_number in sorted(line_numbers):
                        covered_lines.append(lines[line_number - 1])

                print("".join(covered_lines))

        else:
            # If the tests failed, print an error message
            print("Tests failed, coverage data is not available")


def generate_for_git_history():
    while test_directory.exists() and source_directory.exists():
        add_example(test_directory, source_directory)
        result = subprocess.run(
            ['git', 'checkout', 'HEAD^'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        if result.returncode != 0:
            raise Exception(result.stderr.decode())
