# Efnet

## Introduction
Efnet is an high-performance FPGA-based NIC and plaftform for in-network compute.

Efnet currently only supports devices from Xilinx. Designs are included for 
the following FPGA boards:

- Xilinx Alveo U200 (Xilinx Virtex UltraScale+ XCU200)

Operation at 100G on Xilinx UltraScale+ devices currently requires using the Xilinx CMAC core with RS-FEC enabled, which is covered by the free CMAC license.

# Prerequirements
## OS system
`Efnet` has only been tested on Linux, so it is the recommended operating system.

## Build environment

### Chisel installation

#### Install Java
Scala runs on the Java Virtual Machine (JVM), so it is necessary to install a JDK to use Chisel. Chisel works on any version of Java version 8 or newer; however, we recommend using an LTS release version 17 or newer

```shell
# centos 7.9
yum install java-11-openjdk
# ubuntu 20.04
sudo apt install openjdk-11-jre-headless
sudo apt install openjdk-11-jdk-headless
```

#### Install scala
`Efnet` requires scala version is 2.13.12.
```shell
# download scala 2.13.12
wget https://downloads.lightbend.com/scala/2.13.12/scala-2.13.12.tgz
tar -xvf scala-2.13.12 -C /user/local/share
export PATH="$PATH:/usr/local/share/scala-2.13.12/bin"
```
#### Install mill
After you have the mill installed for the first time, you need to run `mill setup` to download some dependencies.
```shell
curl -L https://raw.githubusercontent.com/lefou/millw/0.4.11/millw > mill && chmod +x mill
sudo mv mill /usr/local/bin/
```

# Testing
Running the included testbenches requires [cocotb](https://github.com/cocotb/cocotb), [cocotb-test](https://github.com/themperek/cocotb-test) and [Synopsys vcs](https://www.synopsys.com/verification/simulation/vcs.html).

## Custom test cases
All the test cases are defined in 'cocotb_test.toml', allowing you to disable or customize specific ones as needed.

```toml
[[tests]] # declare that there are test cases for testing a single module
package = "efnet.utils" # the package name of the module
object = "ParityGenerator" # module name
test = "test_parity_generator" # the cocotb test file used to test the module. the path to search the file depends on the package name. In this case, the test script will search for the `test_parity_generator` from the `cocotb/efnet/utils/` directory. 

# Module parameters, allowing to set multiple groups of parameters, the test script will automatically generate a test case for each group of parameters.
params = [ 
  {"parity" = 0 },
  {"parity" = 1 },
  {"parity" = 2 },
]
disable = true # Whether to disable these test cases
```

## Start testing
Go to the root directory and run `make test` to start testing.


# Mill setup
```shell
# In VSCode with the Metals IDE, you'll need to install the Bloop extension to manage Scala projects using Mill. To install the Bloop extension, run the following command from your working directory:
mill --import "ivy:com.lihaoyi::mill-contrib-bloop:" mill.contrib.bloop.Bloop/install
```

# Python environment
```shell
pip3 install cocotb cocotb_test pytest
```

# Compile efnet
```shell
make
```

# Test
efnet driven test by using cocotb

```shell
export SIM = "vcs" # you can use other simulator, e.g. verilator
make test
```