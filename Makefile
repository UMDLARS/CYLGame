.PHONY: format
format:
	pipenv run isort --settings-path pyproject.toml .
	pipenv run black --config pyproject.toml .
