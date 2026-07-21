.PHONY: check check-source test install-preview install

check: test
	python3 scripts/validate.py

check-source: test
	python3 scripts/validate.py --source-only

test:
	python3 -m unittest discover -s tests -v

install-preview:
	python3 scripts/install.py

install:
	python3 scripts/install.py --apply
