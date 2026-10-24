.PHONY: check check-source test install-preview install wezterm-preview wezterm skills-preview skills

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

wezterm-preview:
	python3 scripts/install_wezterm.py

wezterm:
	python3 scripts/install_wezterm.py --apply

skills-preview:
	python3 scripts/install_skills.py

skills:
	python3 scripts/install_skills.py --apply
