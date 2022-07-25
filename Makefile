test: unit integ

unit:
	pytest tests/ checkpointing/

ws = 0.1

integ:
	python -m integtests.run $(kw) --wait-sec $(ws)

doc: mandoc apidoc

mandoc-serve:
	mkdocs serve

mandoc:
	mkdocs build

apidoc:
	pdoc checkpointing -o ./apidoc --docformat google
