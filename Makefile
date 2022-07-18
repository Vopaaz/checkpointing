test: unit integ

unit:
	pytest tests/ checkpointing/

integ:
	python -m integtests.run

doc: mandoc apidoc

mandoc-serve:
	cd docs && mkdocs serve

mandoc:
	cd docs && mkdocs build

apidoc:
	pdoc checkpointing -o ./apidoc --docformat google
