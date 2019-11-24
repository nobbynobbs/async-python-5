
lint:
	poetry run flake8 --exclude=lib

mypy:
	poetry run mypy --ignore-missing-imports minechat

