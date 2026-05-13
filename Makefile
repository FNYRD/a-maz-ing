install:
	python3 -m venv venv
	venv/bin/pip install --upgrade pip
	venv/bin/pip install -r requirements.txt
	venv/bin/python -m build --wheel --outdir .
	venv/bin/pip install mazegen-*.whl

run:
	venv/bin/python a_maze_ing.py config.txt

debug:
	venv/bin/python -m pdb a_maze_ing.py config.txt

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .mypy_cache -exec rm -rf {} +
	find . -type d -name .flake8_cache -exec rm -rf {} +
	find . -type d -name mazegen.egg-info -exec rm -rf {} +
	find . -type d -name build -exec rm -rf {} +

lint:
	venv/bin/flake8 --exclude=.venv,mlx,build --filename='*.py' .
	venv/bin/mypy --warn-return-any \
		 --warn-unused-ignores \
		 --ignore-missing-imports \
		 --disallow-untyped-defs \
		 --check-untyped-defs \
		 --exclude '^(venv|\.venv|env|mlx|build)/' .

lint-strict:
	venv/bin/flake8 --exclude=.venv,mlx,build --filename='*.py' .
	venv/bin/mypy --strict \
		--exclude '^(venv|\.venv|env|mlx|build)/' .

.PHONY: install run debug clean lint lint-strict
