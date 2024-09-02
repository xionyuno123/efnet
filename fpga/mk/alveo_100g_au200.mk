BUILD_DIR := $(CURDIR)
ROOT_DIR := $(BUILD_DIR)/..

# FPGA settings
MAKEFILE=$(ROOT_DIR)/mk/alveo_100g_au200.mk
FPGA_TOP=Uart
FPGA_PART=xcu200-fsgd2104-2-e
FPGA_ARCH=virtexuplus
FPGA_FLASH=true

# Files for synthesis
SYN_FILES += rtl/Uart.sv
SYN_FILES += rtl/BuadRateGenerator.sv
SYN_FILES += rtl/ClockDivider.sv
SYN_FILES += rtl/phase_locked_loop.v
SYN_FILES += rtl/UartRx.sv
SYN_FILES += rtl/UartTx.sv

# XDC files
XDC_FILES += xdc/alveo_100g_au200.xdc

# IP
IP_TCL_FILES += ip/clk_wiz.tcl

# IP XCI Files
# XCI_FILES +=  

# Config TCL files
# CONFIG_TCL_FILES = ./config.tcl

include $(ROOT_DIR)/mk/vivado.mk
include $(ROOT_DIR)/mk/common.mk
