import json

with open(
        "example/test_example.py"
) as f:
    prompt = f.read()

with open(
        "example/example.py"
) as f:
    completion = f.read()

with open("example.jsonl", "w+") as f:
    f.write(json.dumps({"prompt": prompt, "completion": completion}))
