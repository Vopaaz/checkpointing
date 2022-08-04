.PHONY: test unit integ doc mandoc-serve mandoc apidoc

test: unit integ

unit:
	pytest tests/ checkpointing/

ws = 0.2

integ:
	python -m integtests.run $(kw) --wait-sec $(ws)

mandoc-serve: apidoc
	mkdocs serve

mandoc: apidoc
	mkdocs build

apidoc:
	rm -rf ./docs/apidoc
	pdoc checkpointing -o ./docs/apidoc --docformat google
