# PostgreSQL Chinese message catalogs.
# Checks cover zh_CN/ and zh_TW/; packaging targets use zh_CN/.
# Python 3 and GNU gettext suffice; only fetch-upstream touches the network.

BRANCHES := master REL_18_STABLE REL_17_STABLE REL_16_STABLE REL_15_STABLE REL_14_STABLE
SNAPSHOT ?= $(lastword $(sort $(wildcard tmp/upstream-*)))
BRANCH   ?= master
CATALOG  ?= postgres

.DEFAULT_GOAL := help
.PHONY: help check check-align stats mo dist redmine fetch-upstream diff show clean

help:  ## List the available targets
	@grep -hE '^[a-z-]+:.*?##' $(MAKEFILE_LIST) | awk -F':.*?## ' '{printf "  \033[1m%-16s\033[0m %s\n", $$1, $$2}'
	@echo
	@echo "  Variables: BRANCH=$(BRANCH)  CATALOG=$(CATALOG)  SNAPSHOT=$(if $(SNAPSHOT),$(SNAPSHOT),<none yet; run make fetch-upstream>)"

check:  ## Validate all 324 catalogs: msgfmt, completeness, headers, alignment
	@python3 bin/check.py
	@python3 bin/check.py --language zh_TW
	@python3 bin/check-align.py
	@python3 bin/check-align.py --language zh_TW

check-align:  ## Check terminal column alignment by East Asian display width
	@python3 bin/check-align.py
	@python3 bin/check-align.py --language zh_TW

stats:  ## Show message counts per catalog per branch
	@python3 bin/stats.py

mo:  ## Compile every catalog to .mo under build/<branch>/zh_CN/LC_MESSAGES/
	@for b in $(BRANCHES); do \
	  mkdir -p build/$$b/zh_CN/LC_MESSAGES; \
	  for f in zh_CN/$$b/*.po; do \
	    msgfmt -o build/$$b/zh_CN/LC_MESSAGES/$$(basename $$f .po).mo $$f || exit 1; \
	  done; \
	  echo "  $$b  $$(ls build/$$b/zh_CN/LC_MESSAGES | wc -l | tr -d ' ') catalogs"; \
	done

dist:  ## Build release assets into dist/: six branch zips, a tarball, SHA256SUMS
	@bash bin/mkdist.sh

redmine:  ## Lay out catalogs as <catalog>-zh_CN.po per branch, for the patch tracker
	@bash bin/mkredmine.sh

fetch-upstream:  ## Download a fresh zh_CN snapshot from babel into tmp/upstream-<date>/
	@bash bin/fetch-upstream.sh

diff:  ## Compare zh_CN/ against that snapshot: msgid drift and coverage
	@test -n "$(SNAPSHOT)" || { echo "No snapshot yet. Run: make fetch-upstream"; exit 1; }
	@python3 bin/diff-upstream.py $(SNAPSHOT)

show:  ## Print one catalog's header: make show BRANCH=master CATALOG=psql
	@head -20 zh_CN/$(BRANCH)/$(CATALOG).po

clean:  ## Remove build/ and dist/
	@rm -rf build dist && echo "Removed build/ and dist/"
