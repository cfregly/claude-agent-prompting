PY ?= python3
mcp ?=
url ?=
MCP_TARGET = $(if $(mcp),$(mcp),$(url))
ENV_FILE ?= .env
PROVIDERS ?=
HARNESSES ?=
CONCURRENCY ?= 2
MAX_CASES ?=
OUT ?=

define require_mcp_target
	@if [ -n "$(MCP)$(URL)" ]; then \
		echo "Use lowercase selectors: make $@ mcp=<target> or make $@ url=<repo-url>"; \
		exit 2; \
	fi
	@if [ -z "$(MCP_TARGET)" ]; then \
		echo "Missing target. Use: make $@ mcp=screenpipe or make $@ url=https://github.com/<org>/<repo>"; \
		exit 2; \
	fi
endef

.PHONY: help optimize optimize-dry optimize-grind

help:
	@echo "make optimize mcp=screenpipe                         live stored MCP optimization matrix"
	@echo "make optimize mcp=humwork                            live YC P2026 expert-consultation matrix"
	@echo "make optimize mcp=openwork                           live YC P2026 UI-control matrix"
	@echo "make optimize mcp=insforge                           live YC P2026 backend-agent matrix"
	@echo "make optimize mcp=firecrawl                          live Firecrawl scrape/extract matrix"
	@echo "make optimize mcp=supabase                           live Supabase SQL/migration matrix"
	@echo "make optimize mcp=zymtrace                           live Zymtrace MCP workflow matrix"
	@echo "make optimize mcp=clickhouse                         live ClickHouse read-only guardrail matrix"
	@echo "make optimize mcp=github                             live GitHub MCP guardrail matrix"
	@echo "make optimize mcp=context7                           live Context7 library-resolution matrix"
	@echo "make optimize url=https://github.com/screenpipe/screenpipe"
	@echo "make optimize-dry mcp=screenpipe                     plan cells without provider calls"
	@echo "make optimize-grind mcp=screenpipe                   try one hill-climb candidate"
	@echo "Optional: PROVIDERS=anthropic,openai,gemini HARNESSES=prompt_json OUT=/tmp/report.md"

optimize:
	$(call require_mcp_target)
	$(PY) scripts/optimize_mcp.py "$(MCP_TARGET)" --env-file "$(ENV_FILE)" --live --require-live --markdown --concurrency "$(CONCURRENCY)" $(if $(PROVIDERS),--providers "$(PROVIDERS)",) $(if $(HARNESSES),--harnesses "$(HARNESSES)",) $(if $(MAX_CASES),--max-cases "$(MAX_CASES)",) $(if $(OUT),--out "$(OUT)",)

optimize-dry:
	$(call require_mcp_target)
	$(PY) scripts/optimize_mcp.py "$(MCP_TARGET)" --markdown --concurrency "$(CONCURRENCY)" $(if $(PROVIDERS),--providers "$(PROVIDERS)",) $(if $(HARNESSES),--harnesses "$(HARNESSES)",) $(if $(MAX_CASES),--max-cases "$(MAX_CASES)",) $(if $(OUT),--out "$(OUT)",)

optimize-grind:
	$(call require_mcp_target)
	$(PY) scripts/optimize_mcp.py "$(MCP_TARGET)" --env-file "$(ENV_FILE)" --live --require-live --grind --markdown --concurrency "$(CONCURRENCY)" $(if $(PROVIDERS),--providers "$(PROVIDERS)",) $(if $(HARNESSES),--harnesses "$(HARNESSES)",) $(if $(MAX_CASES),--max-cases "$(MAX_CASES)",) $(if $(OUT),--out "$(OUT)",)
