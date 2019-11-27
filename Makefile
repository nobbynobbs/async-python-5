install:
	poetry install --no-dev

install-dev:
	poetry install

lint:
	poetry run flake8 --exclude=lib

mypy:
	poetry run mypy --config-file mypy.ini -p minechat

test:
	poetry run pytest tests
