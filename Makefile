build:
	docker build -t wisecloud_upgrader .

test:
	-docker rm -f test
	docker run -it --name test -v ${PWD}/conf:/code/conf    -v ${PWD}/backup:/backup wisecloud_upgrader:latest sh

run:
	-docker rm -f upgrader
	docker run -d --name upgrader -v ${PWD}/conf:/code/conf -v ${PWD}/backup:/backup wisecloud_upgrader:latest
	docker logs -f upgrader