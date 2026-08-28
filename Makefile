SHELL := bash

all:
	@echo "usage to come"
clean:
	@if [ -f *db ]; then rm -v *db; fi
	@if [ -f *log.gz ]; then rm -v *log.gz; fi
	@find -type d | grep '__pycache__$$' | while read dir; do rm -v -rf "$$dir"; done
