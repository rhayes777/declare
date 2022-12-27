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


class Processor:
    def __init__(self, source_directory, test_directory):
        self.source_directory = source_directory
        self.test_directory = test_directory

    def lines(self):
        all_lines = []

        for path in self.test_directory.rglob('test_*.py'):
            file_processor = FileProcessor(path, self.source_directory)
            all_lines.extend(file_processor.lines())

        return all_lines


class FileProcessor:
    def __init__(self, path, source_directory):
        self.path = path
        self.source_directory = source_directory

    def _full_test(self, test_function):
        with open(self.path) as f:
            lines = f.readlines()

        found = False
        found_lines = []

        for line in lines:
            if found and not line.startswith(" "):
                break

            if line.startswith(f"def {test_function}"):
                found = True

            if found:
                found_lines.append(line)

        return "".join(found_lines)

    def lines(self):
        lines = []
        for test_function in [f for f in dir(importlib.import_module(".".join(self.path.with_suffix("").parts))) if
                              f.startswith("test_")]:
            test = self._full_test(test_function)
            completion = self.completion_for_test(test_function)

            lines.append({"prompt": test, "completion": completion})
        return lines

    def completion_for_test(self, test_function):
        # Run the tests with the `--cov` option to collect coverage data
        result = pytest.main([str(self.path), "-k", test_function, f"--cov={self.source_directory}"])

        file_results = []

        # Check the exit code of the test run
        if result == 0:
            print(f"Test run for {self.path}.{test_function} was successful")

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

                    extra_lines = set()
                    for line_number in line_numbers:
                        position = line_number - 1
                        while position >= 0:
                            position -= 1
                            if position < 0:
                                break

                            extra_lines.add(position)

                            line = lines[position]
                            if line[0] != " ":
                                break

                    for line_number in sorted({*line_numbers, *extra_lines}):
                        covered_lines.append(lines[line_number - 1])

                content = "".join(covered_lines)
                file_results.append(f"> {file}\n{content}")

        else:
            # If the tests failed, print an error message
            print("Tests failed, coverage data is not available")

        return "\n".join(file_results)


def main():
    args = parser.parse_args()
    test_directory = args.test
    source_directory = args.source

    sys.path.append(str(source_directory.parent))

    processor = Processor(source_directory, test_directory)
    print(processor.lines())


if __name__ == "__main__":
    main()


def generate_for_git_history(test_directory, source_directory):
    while test_directory.exists() and source_directory.exists():
        add_example(test_directory, source_directory)
        result = subprocess.run(
            ['git', 'checkout', 'HEAD^'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        if result.returncode != 0:
            raise Exception(result.stderr.decode())
