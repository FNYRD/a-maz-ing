install:
	poetry install

run:
	poetry run python3 a_maze_ing.py

debug:
	poetry run python3 -m pdb a_maze_ing.py

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .mypy_cache -exec rm -rf {} +
	find . -type d -name .flake8_cache -exec rm -rf {} +

lint:
	flake8 .
	mypy --warn-return-any \
		 --warn-unused-ignores \
		 --ignore-missing-imports \
		 --disallow-untyped-defs \
		 --check-untyped-defs .

lint-strict:
	flake8 . --strict
	mypy . --strict

.PHONY: install run debug clean lint lint-strict