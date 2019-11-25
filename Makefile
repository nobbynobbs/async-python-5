
lint:
	poetry run flake8 --exclude=lib

mypy:
	poetry run mypy --config-file mypy.ini -p minechat
