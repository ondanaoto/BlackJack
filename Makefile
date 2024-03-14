lint:
	flake8 src
	isort --check --diff src
	black --check src

format:
	isort src
	black src
