import json
from json import JSONDecodeError
from .schema import PaperSummary

class ValidatorAgent:
    def validate(self, raw_output: str):
        if not raw_output or not raw_output.strip():
            raise ValueError("LLM returned empty response")

        try:
            data = json.loads(raw_output)
        except JSONDecodeError as e:
            raise ValueError(f"JSON syntax error: {str(e)}")

        try:
            validated = PaperSummary(**data)
        except Exception as e:
            raise ValueError(f"Schema validation error: {str(e)}")

        return validated.model_dump()
