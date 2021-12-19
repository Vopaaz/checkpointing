apidoc:
	pdoc checkpointing -o ./docs/api --docformat google

test:
	nosetests --with-coverage --cover-package=checkpointing --with-doctest tests/**/*.py checkpointing/**/*.py
