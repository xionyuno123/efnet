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