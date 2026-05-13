install:
	python3 -m venv .venv
	source ./venv/bin/activate
	pip3 install --upgrade pip setuptools wheel
	pip3 install -r requirements.txt
	python3 -m build --wheel --outdir .
	pip3 install mazegen-*.whl
	deactivate

run:
	source ./venv/bin/activate
	python3 a_maze_ing.py config.txt
	deactivate

debug:
	source ./venv/bin/activate
	python3 -m pdb a_maze_ing.py config.txt
	deactivate

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .mypy_cache -exec rm -rf {} +
	find . -type d -name .flake8_cache -exec rm -rf {} +
	find . -type d -name mazegen.egg-info -exec rm -rf {} +
	find . -type d -name build -exec rm -rf {} +

lint:
	source ./venv/bin/activate
	flake8 --exclude=.venv,mlx,build --filename='*.py' .
	mypy --warn-return-any \
		 --warn-unused-ignores \
		 --ignore-missing-imports \
		 --disallow-untyped-defs \
		 --check-untyped-defs \
		 --exclude '^(venv|\.venv|env|mlx|build)/' .
	deactivate

lint-strict:
	source ./venv/bin/activate
	flake8 --exclude=.venv,mlx,build --filename='*.py' .
	mypy  --strict \
		--exclude '^(venv|\.venv|env|mlx|build)/' .
	deactivate

.PHONY: install run debug clean lint lint-strict
