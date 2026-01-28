.PHONY: build run

build:
	uv run python build.py

run:
	./dist/photo-sorter $(ARGS)
