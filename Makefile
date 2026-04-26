.PHONY: build run

# `make run -- ./some/dir` passes ./some/dir as an extra goal, not as $(ARGS).
RUN_ARGS := $(filter-out run,$(MAKECMDGOALS))

build:
	uv run python build.py

run:
	./dist/photo-sorter $(ARGS) $(RUN_ARGS)

ifneq ($(strip $(RUN_ARGS)),)
.PHONY: $(RUN_ARGS)
$(RUN_ARGS):
	@:
endif
