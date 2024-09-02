
# FPGA settings
MAKEFILE = alveo_100g_au200.mk
FPGA_TOP = Uart
FPGA_PART = xcu200-fsgd2104-2-e
FPGA_ARCH = virtexuplus
FPGA_FLASH = true

# Files for synthesis
SYN_FILES = rtl/Uart.sv

# XDC files
# XDC_FILES = 

# IP
IP_TCL_FILES = ip/clk_wiz.tcl

# IP XCI Files
# XCI_FILES = 

# Config TCL files
# CONFIG_TCL_FILES = ./config.tcl

include vivado.mk
include common.mk

