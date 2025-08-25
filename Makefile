MAKEFLAGS += -B

venv:
	python3 -m venv --clear venv
	./venv/bin/python -m pip install -r requirements.txt

beautify:
	pnpm exec prettier ${PWD}/index.html --write
	./venv/bin/isort main.py
	./venv/bin/black main.py

ip:
	ip -br -4 a

dev: ip
	./venv/bin/hypercorn main:app --reload
