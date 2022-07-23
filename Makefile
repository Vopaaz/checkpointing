test: unit integ

unit:
	pytest tests/ checkpointing/

ws = 0.1

integ:
	python -m integtests.run $(kw) --wait-sec $(ws)

doc: mandoc apidoc readme

mandoc-serve:
	cd docs && mkdocs serve

mandoc:
	cd docs && mkdocs build

apidoc:
	pdoc checkpointing -o ./apidoc --docformat google
