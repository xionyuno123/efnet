import argparse
import pathlib
import tomllib
from gen_system_verilog import ChiselModule,SVGenerator
from test_fpga import CocotbChiselTest,CocotbChiselTestGroup
import subprocess

class FpgaBuilder():
  enable_build:bool
  fpga_dir:pathlib.Path
  fpga_variant: str
  fpga_board:str
  fpga_name:str
  fpga_params:dict

  test_toml:pathlib.Path
  enable_test:bool

  def __init__(self,fpga_dir:pathlib.Path,enable_build:bool,enable_test:bool):
    self.fpga_dir = fpga_dir
    toml_file = fpga_dir / "build.toml"
    with open(toml_file,"r") as f:
      config = tomllib.load(f)
      build = config.get("build")
      if build is None:
        raise ValueError(f"build setting is not found in the {toml_file} file")
      if not isinstance(build,dict):
        raise ValueError(f"invalid build field in the file {toml_file}")
      self.fpga_board = build.get("board")
      if self.fpga_board is None:
        raise ValueError(f"build.board is not found in the file {toml_file}")
      if not isinstance(self.fpga_board,str):
        raise ValueError(f"build.board field is not a string")

      self.fpga_variant = build.get("variant")
      if self.fpga_variant is None:
        raise ValueError(f"build.variant is not found in the file {toml_file}")
      if not isinstance(self.fpga_board,str):
        raise ValueError(f"build.variant field is not a string")

      self.fpga_name = build.get("fpga")
      if self.fpga_name is None:
        raise ValueError(f"build.fpga is not found in the file {toml_file}")
      if not isinstance(self.fpga_board,str):
        raise ValueError(f"build.fpga field is not a string")
      
      self.fpga_params = build.get("params")
      if self.fpga_params is not None and not isinstance(self.fpga_params,dict):
        raise ValueError(f"build.params is not a dict")
      
      test = config.get("test")
      if test is None:
        self.simulator = "vcs"
        self.allowlist = []
        self.blacklist = []
      else:
        simulator = "vcs" if test.get("simulator") is None else test.get("simulator")
        if not isinstance(simulator,str):
          raise ValueError("test.simulator is not a string")
        allowlist = "" if test.get("allowlist") is None else test.get("allowlist")
        if not isinstance(allowlist,str):
          raise ValueError("test.allowlist is not a string")
        for entry in allowlist.split(";"):
          self.allowlist.append(entry)
        blacklist = "" if test.get("allowlist") is None else test.get("blacklist")
        if not isinstance(blacklist,str):
          raise ValueError("test.blacklist is not a string")
        for entry in blacklist.split(";"):
          self.blacklist.append(entry)
        
        if len(self.blacklist) != 0 and len(self.allowlist) != 0:
          raise ValueError("test.allowlist and test.blacklist can not be set at the same time")

      self.test_toml = fpga_dir / "test.toml"
      self.enable_build = enable_build
      self.enable_test = enable_test
 
  def build(self):
    # if enable tests
    if self.enable_test:
      groups = CocotbChiselTestGroup(self.simulator,self.fpga_dir/"tb",self.fpga_dir)
      with open(self.fpga_dir/"test.toml","r") as f:
        config = tomllib.load(f)
        for test in config.get("tests"):
          groups.add_test(CocotbChiselTest(test))
      for pattern in self.allowlist:
        groups.add_allowlist(pattern=pattern)
      for pattern in self.blacklist:
        groups.add_blacklist(pattern=pattern)
      groups.run()

    if not self.enable_build:
      return
    
    # generate systemverilog
    module_name = f"efnet.nic.{self.fpga_board}.{self.fpga_variant}.{self.fpga_name}.EfnetNic"
    module = ChiselModule(name=module_name,target_dir=self.fpga_dir/"rtl",params=self.fpga_params)
    sv_gen = SVGenerator(self.fpga_dir,modules=[module])
    sv_gen.gen("rtlbuild")

    # build bitstream
    cmd = subprocess.run(["make","-f",f"{self.fpga_board}_{self.fpga_variant}_{self.fpga_name}.mk","all"],cwd=self.fpga_dir/"mk")
    cmd.check_returncode()

parser = argparse.ArgumentParser(description = "Used to build fpga")
parser.add_argument("--dir",type = str,required=True,help="source path")
parser.add_argument("--enable-test",type=bool,default=False,help="enable tests")
parser.add_argument("--enable-build",type=bool,default=False,help="enable build")

args = parser.parse_args()

builder = FpgaBuilder(pathlib.Path(args.toml).absolute())
builder.build()