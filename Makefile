all:
	@echo "usage to come"
clean:
	rm *db
	rm *log.gz
	find -type d | grep '__pycache__' |while read dir; do rm -rf $dir; done
