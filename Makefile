apidoc:
	pdoc checkpointing -o ./docs/api --docformat google

test:
	pytest tests/ checkpointing/

integ:
	python -m integtests.run
