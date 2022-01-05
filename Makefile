PROJECT_NAME=gmail_analytics_check
LINT_FILES=gmail_analytics_check tests

test:
	coverage run --source=./gmail_analytics_check -m pytest tests
	coverage report -m
	coverage html

rerun-tests:
	pytest --lf -vv

lint:
	@echo 'syntax errors or undefined names'
	flake8 --count --select=E9,F63,F7,F82 --show-source --statistics ${LINT_FILES}
	@echo 'warning'
	flake8 --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics --ignore=E731,W503,E501 ${LINT_FILES}

	@echo 'mypy'
	mypy ${LINT_FILES}

format:
	@echo 'black'
	black --skip-string-normalization ${LINT_FILES}

clean:
	rm -rf reports htmcov dist build *.egg-info *.txt *.csv *.pdf

install:
	pip3 install .

rename:
	@python3 update.py