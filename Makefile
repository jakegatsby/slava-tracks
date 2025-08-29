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

postgres:
	docker run --name slava-tracks-postgres -e POSTGRES_PASSWORD=mysecretpassword -p 5432:5432 postgres

debug: ip
	DATABASE_URL=postgresql://postgres:mysecretpassword@localhost:5432/postgres ./venv/bin/flask --app slavatracks/ run --debug

run: ip
	DATABASE_URL=postgresql://postgres:mysecretpassword@localhost:5432/postgres ./venv/bin/gunicorn --bind "[::]:5000" "slavatracks:create_app()"
