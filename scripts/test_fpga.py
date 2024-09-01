import pathlib
import shutil
import re
import subprocess
import multiprocessing
import json
from gen_system_verilog import ChiselModule,SVGenerator

def mname2fname(module_name:str) -> str:
  file_name = ""
  entries = module_name.split(".")
  for entry in entries:
    file_name = entry + "_"
  if len(file_name) != 0:
    file_name = file_name[:-1]
  return file_name
  
def toplevel(module_name:str) -> str:
  entries = module_name.split(".")
  return entries[-1]

class CocotbChiselTest():
  module:str
  params:list[dict]
  timescale:str
  waves:bool

  def __init__(self,test:dict):
    self.module = test.get("module")
    self.params = test.get("params")
    self.timescale = test.get("timescale")
    self.waves = test.get("waves")

    if self.module is None:
      raise ValueError("test.module not given")
    if self.timescale is None:
      self.timescale = "1ns/1ps"
    if self.waves is None:
      self.waves = False
    
  def chisel_modules(self,out_dir:pathlib.Path) -> list[ChiselModule]:
    if not out_dir.exists():
      out_dir.mkdir(parents=True)

    modules = []
    test_id = 0
    for param in self.params:
      target_dir = out_dir / f"{mname2fname(self.module)}" / f"test{test_id}"
      if not target_dir.exists():
        target_dir.mkdir(parents=True)
      module = ChiselModule(self.module,target_dir=target_dir,params=param)
      modules.append(module)
    
    return modules
  
  def gen_test(self,sim:str,tb_dir:pathlib.Path,out_dir:pathlib.Path):
    if not tb_dir.is_dir():
      raise ValueError(f"{tb_dir} not a directory")
    test_id = 0
    for param in self.params:
      paramstr = json.dump(param)
      target_dir = out_dir / f"{mname2fname(self.module)}" / f"test{test_id}"
      if not target_dir.exists():
        target_dir.mkdir(parent=True)
      with open(target_dir/f"test_{mname2fname(self.module)}_param{test_id}.py","w") as f:
        f.write(f"""import sys
                import pathlib
                import pytest
                import cocotb
                import cocotb_test.simulator
                sys.path.append(f"{{pathlib.Path(__file__).absolute().parent.parent.parent.parent}}")
                from test_{mname2fname(self.module)} import cocotb_chisel_test

                class TestParams:
                  __params__:dict
                  def __init__(self,params:dict):
                    self.__params__ = params
                  def __getattr__(self, name: str) -> any:
                    return self.__params__.get(name)
                
                @pytest.mark.trylast
                def test_uart_param{test_id}():
                  cocotb_test.simulator.run(
                    simulator = "{sim}",
                    toplevel = "{toplevel(self.module)}",
                    module = "test_{mname2fname(self.module)}_param{test_id}.py",
                    toplevel_lang = "verilog",
                    timescale = "{self.timescale}",
                    waves = {self.waves},
                    gui = False,
                  )

                @cocotb.test()
                async def cocotb_test_{mname2fname(self.module)}_param{test_id}(dut):
                  params = TestParams({paramstr})
                  await cocotb_chisel_test(dut,params)
""")
      
    
class CocotbChiselTestGroup():
  tb_dir:pathlib.Path
  out_dir:pathlib.Path
  simulator:str
  source_dir:pathlib.Path
  cocotb_chisel_tests:list[CocotbChiselTest]
  allowlist:list[re.Pattern]
  blacklist:list[re.Pattern]

  def __init__(self,simulator:str,tb_dir:pathlib.Path,source_dir:pathlib.Path):
    tb_dir = tb_dir.absolute()
    source_dir = source_dir.absolute()

    if not tb_dir.exists():
      tb_dir.mkdir(parents=True)
    if not tb_dir.is_dir():
      raise ValueError(f"{tb_dir} not a directory")
    
    self.out_dir = tb_dir / "out"

    if self.out_dir.is_dir():
      shutil.rmtree(self.rtl_dir)

    if not self.out_dir.exists():
      self.out_dir.mkdir(parents=True)
    if not self.out_dir.is_dir():
      raise ValueError(f"{self.out_dir} not a directory")
    
    if not source_dir.exists():
      raise ValueError(f"{source_dir} not found")
    if not source_dir.is_dir():
      raise ValueError(f"{source_dir} not a directory")
    
    self.simulator = "vsc" if simulator is None else simulator
    self.tb_dir = tb_dir
    self.source_dir = source_dir
    self.cocotb_chisel_tests = []
    self.allowlist = []
    self.blacklist = []

  def add_allowlist(self,pattern:str):
    self.allowlist.appen(rf"{pattern}")
  
  def add_blacklist(self,pattern:str):
    self.blacklist.append(rf"{pattern}")
  
  def add_test(self,test:CocotbChiselTest):
    self.cocotb_chisel_tests.append(test)

  def allow_test(self,test:CocotbChiselTest) -> bool :
    # enable all
    if len(self.allowlist) == 0 and len(self.blacklist) == 0:
      return True
    
    if len(self.allowlist) != 0:
      for pattern in self.allowlist:
        if pattern.match(test.module):
          return True
      return False

    if len(self.blacklist) != 0:
      for pattern in self.blacklist:
        if pattern.match(test.module):
          return False
      return True
        
  def run(self):
    # clean out_dir
    if self.out_dir.is_dir():
      shutil.rmtree(self.out_dir)

    # generate systemverilog and test cases
    modules = []
    for test in self.cocotb_chisel_tests:
      if self.allow_test(test):
        modules.append(test.chisel_modules())
        test.gen_test(self.simulator,self.tb_dir,self.out_dir)
    sv_gen = SVGenerator(self.source_dir,modules=modules)
    sv_gen.gen("rtlbuild")

    # run test cases
    cmd = subprocess.run(["pytest","-n",f"{multiprocessing.cpu_count()}",f"{self.out_dir}"])
    cmd.check_returncode()
    
