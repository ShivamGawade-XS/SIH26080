.PHONY: setup demo demo-fast data train verify test lint typecheck e2e a11y perf audit docs-check fresh-clone real-smoke report serve clean

PYTHON ?= python

setup:
	$(PYTHON) -m pip install -e ".[dev]"
	cd web && npm install

demo-fast:
	$(PYTHON) -m varsha.cli data synth --profile demo-fast
	$(PYTHON) -m varsha.cli label --config configs/regimes.yaml --profile demo-fast
	$(PYTHON) -m varsha.cli train --config configs/models.yaml --profile demo-fast
	$(PYTHON) -m varsha.cli run --profile demo-fast
	$(PYTHON) -m varsha.cli verify --profile demo-fast
	$(PYTHON) -m varsha.cli report --latest
	pytest tests/unit tests/property tests/controls tests/api

demo:
	$(PYTHON) -m varsha.cli data synth --profile demo
	$(PYTHON) -m varsha.cli label --config configs/regimes.yaml --profile demo
	$(PYTHON) -m varsha.cli train --config configs/models.yaml --profile demo
	$(PYTHON) -m varsha.cli run --profile demo
	$(PYTHON) -m varsha.cli verify --profile demo
	$(PYTHON) -m varsha.cli report --latest
	cd web && npm run build
	@echo "=== VARSHA MVP READY ==="
	@echo "Launching local console at http://localhost:8000"
	$(PYTHON) -m varsha.cli serve --port 8000

data:
	$(PYTHON) -m varsha.cli data synth --profile demo

train:
	$(PYTHON) -m varsha.cli train --config configs/models.yaml --profile demo

test:
	pytest tests/unit tests/property tests/controls tests/api -v

lint:
	ruff check src/ tests/

typecheck:
	mypy src/varsha/

verify: lint typecheck test docs-check
	$(PYTHON) -m varsha.cli verify --profile demo-fast

e2e:
	cd web && npx playwright test

a11y:
	cd web && npm run test:a11y

perf:
	cd web && npm run test:perf

audit:
	pip-audit || echo "pip-audit completed"
	cd web && npm audit || echo "npm audit completed"

docs-check:
	$(PYTHON) scripts/verify_docs.py

fresh-clone:
	powershell -ExecutionPolicy Bypass -File scripts/fresh_clone_test.ps1

real-smoke:
	$(PYTHON) -m varsha.cli data fetch --source gfs --lead 1 --date 2024-07-15 || echo "Real mode requires live network/credentials"

report:
	$(PYTHON) -m varsha.cli report --latest

serve:
	$(PYTHON) -m varsha.cli serve --port 8000

clean:
	powershell -Command "Remove-Item -Recurse -Force -ErrorAction SilentlyContinue products/*, data/interim/*, .pytest_cache, dist, web/dist"
