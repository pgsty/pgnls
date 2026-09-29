# PostgreSQL Chinese message catalogs.
# Checks and packaging cover zh_CN/ and zh_TW/.
# Python 3 and GNU gettext are required; dist also needs GNU tar and gzip.
# Only fetch-upstream touches the network.

BRANCHES := master REL_18_STABLE REL_17_STABLE REL_16_STABLE REL_15_STABLE REL_14_STABLE
LANGUAGES := zh_CN zh_TW
SNAPSHOT ?= $(lastword $(sort $(wildcard tmp/upstream-*)))
BRANCH   ?= master
CATALOG  ?= postgres

.DEFAULT_GOAL := help
.PHONY: help check check-align stats mo dist redmine fetch-upstream diff show clean

help:  ## List the available targets
	@grep -hE '^[a-z-]+:.*?##' $(MAKEFILE_LIST) | awk -F':.*?## ' '{printf "  \033[1m%-16s\033[0m %s\n", $$1, $$2}'
	@echo
	@echo "  Variables: BRANCH=$(BRANCH)  CATALOG=$(CATALOG)  SNAPSHOT=$(if $(SNAPSHOT),$(SNAPSHOT),<none yet; run make fetch-upstream>)"
	@echo "  Release environment: STAMP (YYYYMMDD), DIST (dist/<STAMP>), OUT (<DIST>/redmine), SOURCE_DATE_EPOCH (HEAD commit time)"

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

mo:  ## Compile both languages under build/<branch>/<language>/LC_MESSAGES/
	@for b in $(BRANCHES); do \
	  for lang in $(LANGUAGES); do \
	    mkdir -p build/$$b/$$lang/LC_MESSAGES || exit 1; \
	    for f in $$lang/$$b/*.po; do \
	      msgfmt -o build/$$b/$$lang/LC_MESSAGES/$$(basename $$f .po).mo $$f || exit 1; \
	    done; \
	    echo "  $$b $$lang  $$(ls build/$$b/$$lang/LC_MESSAGES | wc -l | tr -d ' ') catalogs"; \
	  done; \
	done

dist:  ## Build 15 bilingual/monolingual tarballs and SHA256SUMS in dist/<STAMP>/
	@bash bin/mkdist.sh

redmine:  ## Copy both languages as <catalog>-<language>.po into release redmine/
	@bash bin/mkredmine.sh

fetch-upstream:  ## Download a fresh zh_CN snapshot from babel into tmp/upstream-<date>/
	@bash bin/fetch-upstream.sh

diff:  ## Compare zh_CN/ against that snapshot: msgid drift and coverage
	@test -n "$(SNAPSHOT)" || { echo "No snapshot yet. Run: make fetch-upstream"; exit 1; }
	@python3 bin/diff-upstream.py $(SNAPSHOT)

show:  ## Print one catalog's header: make show BRANCH=master CATALOG=psql
	@head -20 zh_CN/$(BRANCH)/$(CATALOG).po

clean:  ## Remove compiled build/; keep release assets in dist/
	@rm -rf build && echo "Removed build/; release assets preserved in dist/"
