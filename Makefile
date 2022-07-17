test: unit integ

unit:
	pytest tests/ checkpointing/

integ:
	python -m integtests.run

doc: mandoc apidoc

mandoc:
	cd docs && mkdocs build

apidoc:
	pdoc checkpointing -o ./apidoc --docformat google
