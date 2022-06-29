apidoc:
	pdoc checkpointing -o ./docs/api --docformat google

test:
	nosetests --with-coverage \
			  --cover-erase \
			  --cover-package=checkpointing \
			  --cover-html \
			  --cover-html-dir=.html-coverage \
			  --with-doctest \
			  tests/**/*.py \
			  checkpointing
