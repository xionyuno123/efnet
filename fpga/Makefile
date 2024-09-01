ROOT_DIR := $(abspath ../)

all: 
	 python ${ROOT_DIR}/scripts/build_fpga.py --dir ${ROOT_DIR}/fpga --enable-test --enable-build
	 
test:
	 python ${ROOT_DIR}/scripts/build_fpga.py --dir ${ROOT_DIR}/fpga --enable-test

clean:
	 rm out -rf