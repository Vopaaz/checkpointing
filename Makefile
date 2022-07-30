.PHONY: test unit integ doc mandoc-serve mandoc apidoc

test: unit integ

unit:
	pytest tests/ checkpointing/

ws = 0.2

integ:
	python -m integtests.run $(kw) --wait-sec $(ws)

doc: mandoc apidoc

mandoc-serve:
	mkdocs serve

mandoc:
	mkdocs build

apidoc:
	pdoc checkpointing -o ./apidoc --docformat google
