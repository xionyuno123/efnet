# Efnet for Alveo

## Introduction
This design targets Xilinx Alveo FPGA boards:

- FPGA
  - AU200: xcu200-fsgd2104-2-e

- MAC: Xilinx 100G CMAC

- PHY: 100G CAUI-4 CMAC and internal GTY transceivers

- RAM: 
  - AU200: 64 GB DDR4 2400 (4x 2G x72 DIMM)

## Quick start

### Build FPGA bitstream
RUN `make` in the `fpga_<BOARD>` subdirectory to build the bitstream