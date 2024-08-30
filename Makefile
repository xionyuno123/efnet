base_dir=$(abspath ./)
MILL ?= mill
# TARGET ?= vivado

all: 
	cd $(base_dir) && $(MILL) efnet.compile

test:
	cd $(base_dir) && python cocotb_test.py

clean:
	rm -rf out/