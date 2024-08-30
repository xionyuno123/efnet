# Mill setup
```shell
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