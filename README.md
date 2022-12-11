# Declare

Generate code from tests using GPT-3. Generations are tested and kept if all tests pass. Pretty experimental and only seems to work for fairly basic cases at the moment.

An API key is required from [OpenAI](https://beta.openai.com/docs/quickstart). This should be set as an environment variable `API_KEY`.

## Usage

Simply declare tests in a Python file and then run the script on that file. A new file suffixed with `_generated.py` is created if tests pass successfully.

```bash
./declare.py examples/is_even.py
```
