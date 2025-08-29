MAKEFLAGS += -B

venv:
	python3 -m venv --clear venv
	./venv/bin/python -m pip install -r requirements.txt

lint:
	pnpm exec prettier ${PWD}/slavatracks/templates/index.html --write
	./venv/bin/black slavatracks
	./venv/bin/isort slavatracks/__init__.py
	./venv/bin/pylint -E slavatracks

ip:
	ip -br -4 a

postgres:
	docker run --name slava-tracks-postgres -e POSTGRES_PASSWORD=mysecretpassword -p 5432:5432 postgres

debug: ip
	DATABASE_URL=postgresql://postgres:mysecretpassword@localhost:5432/postgres ./venv/bin/flask --app slavatracks/ run --debug

run: ip
	DATABASE_URL=postgresql://postgres:mysecretpassword@localhost:5432/postgres ./venv/bin/gunicorn --bind "[::]:5000" "slavatracks:create_app()"


tests:
	./venv/bin/python -c 'import slavatracks; url, title, track = slavatracks.get_track_info_from_url("https://tidal.com/browse/track/267393078?u"); print(url, title,track)'
