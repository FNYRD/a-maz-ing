install:
	pip3 install --upgrade pip setuptools wheel
	pip3 install -r requirements.txt
	python3 -m build --wheel --outdir .
	pip3 install mazegen-*.whl

run:
	python3 a_maze_ing.py config.txt

debug:
	python3 -m pdb a_maze_ing.py config.txt

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .mypy_cache -exec rm -rf {} +
	find . -type d -name .flake8_cache -exec rm -rf {} +
	find . -type d -name mazegen.egg-info -exec rm -rf {} +
	find . -type d -name build -exec rm -rf {} +

lint:
	flake8 --exclude=.venv,mlx .
	mypy --warn-return-any \
		 --warn-unused-ignores \
		 --ignore-missing-imports \
		 --disallow-untyped-defs \
		 --check-untyped-defs .
		 --exclude '^(venv|\.venv|env|mlx)/'

lint-strict:
	flake8 . --strict
	mypy . --strict \
	--exclude '^(venv|\.venv|env|mlx)/'

.PHONY: install run debug clean lint lint-strict
