.PHONY: check install-preview install

check:
	python3 scripts/validate.py

install-preview:
	python3 scripts/install.py

install:
	python3 scripts/install.py --apply
