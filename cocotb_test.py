import sys
import tomllib
import pathlib
import subprocess
import multiprocessing

workspace_dir = pathlib.Path(__file__).parent
cocotb_dir = pathlib.Path(__file__).parent / "cocotb"

class CocotbTest:
    test:str
    params:dict

    def __init__(self,test:str,params:dict) -> None:
        self.test = test
        self.params = params
        pass

class EmitVerilogObject:
   package_name:str
   object_name:str
   cocotb_test: list[CocotbTest]

   def __init__(self,package_name:str,object_name:str) -> None:
        self.package_name = package_name
        self.object_name = object_name
        self.cocotb_test = []
        pass
  
   def add_cocotb_test(self,cocotb_test:CocotbTest):
        self.cocotb_test.append(cocotb_test)
        pass


def require_version(version):
    if sys.version_info < version:
        raise ValueError('Python version is too old')
    
def emitVerilog(objs:list[EmitVerilogObject]):
  with open(workspace_dir / "src/main/scala/main.scala","w") as f:
      f.write("package main\n")
      f.write("import chisel3._\n")
      f.write("object Main extends App {\n")
      for obj in objs:
        test_id = 0
        for test in obj.cocotb_test:
          params = "("
          for key in test.params.keys():
            params += f"{key} = {test.params[key]},"
          params = params[:-1]
          params += ")"
          target_dir = workspace_dir / "out" / "cocotb_test"
          entries = obj.package_name.split(".")
          for entry in entries:
            target_dir = target_dir / entry
          target_dir = target_dir / f"{obj.object_name}.dir" / f"test{test_id}"
          f.write(f"  circt.stage.ChiselStage.emitSystemVerilogFile(\n")
          f.write(f"    new {obj.package_name}.{obj.object_name}{params},\n")
          f.write(f"    Array(\"--target-dir\", \"{target_dir}\")\n")
          f.write(f"  )\n")
          test_id += 1
      f.write("}\n")   
  cmd = subprocess.run(["mill","efnet.run"],cwd=workspace_dir)
  if cmd.returncode != 0:
     raise "Failed to execute `mill efnet.run`"

def buildCototbTest(objs:list[EmitVerilogObject]):
    for obj in objs:
      test_id = 0
      for test in obj.cocotb_test:
        param = test.params
        target_test_file = test.test + f"_param{test_id}"
        # create target directory
        target_dir = workspace_dir / "out" / "cocotb_test"
        cocotb_dir = workspace_dir / "cocotb"
        entries = obj.package_name.split(".")
        for entry in entries:
           cocotb_dir = cocotb_dir / entry
           target_dir = target_dir / entry
        target_dir = target_dir / f"{obj.object_name}.dir" / f"test{test_id}"
        verilog_source_dir = target_dir
        target_dir.mkdir(parents=True,exist_ok=True)
        # read cocotb test script
        cocotb_test = ""
        with open(cocotb_dir / f"{test.test}.py","r") as f:
          cocotb_test = f.read()
        # generate cocotb test script
        with open(target_dir / f"{target_test_file}.py","w") as f:
          f.write(cocotb_test)
          f.write(f"\n")
          for key in param.keys():
            keystr = str(key).upper()
            f.write(f"TEST_PARAM_{keystr} = {param[key]}\n")
          f.write(f"\n")
          f.write(f"\n")
          f.write(f"import os\n")
          f.write(f"import json\n")
          f.write(f"import cocotb_test.simulator\n")
          f.write(f"import cocotb\n")
          f.write(f"import pytest")
          f.write(f"\n")
          f.write(f"def run(**kwargs):\n")
          f.write(f"  sim = os.getenv('SIM',default=\"vcs\")\n")
          f.write(f"  waves = None\n")
          f.write(f"  extra_args = []\n")
          f.write(f"  if sim is None:\n")
          f.write(f"    pass\n")
          f.write(f"  elif sim == \"vcs\":\n")
          f.write(f"    waves = True\n")
          f.write(f"  elif sim == \"verilator\":\n")
          f.write(f"    os.environ['SIM'] = \"verilator\"\n")
          f.write(f"    extra_args.extend([\"--trace\",\"--trace-structs\",\"--coverage\"])\n")
          f.write(f"  elif sim == \"icarus\":\n")
          f.write(f"    os.environ['SIM'] = \"icarus\"\n")
          f.write(f"    os.environ[\"WAVES\"] = \"1\"\n")
          f.write(f"  else:\n")
          f.write("    assert False, f\"Unknown simulator {sim}\"\n")
          f.write(f"  if 'extra_args' not in kwargs:\n")
          f.write(f"    kwargs['extra_args'] = []\n")
          f.write(f"  kwargs['extra_args'] += extra_args\n")
          f.write(f"  if waves is not None:\n")
          f.write(f"    kwargs['waves'] = waves\n")
          f.write(f"  print(kwargs)\n")
          f.write(f"  cocotb_test.simulator.run(**kwargs)\n")
          f.write(f"\n")
          f.write(f"\n")
          f.write(f"@pytest.mark.trylast\n")
          f.write(f"def {test.test}_param{test_id}_chisel():\n")
          #  f.write(f"  paramdict = {paramstr}\n")
          f.write(f"  run(\n")
          f.write(f"    verilog_sources = [\"{verilog_source_dir}/{obj.object_name}.sv\"],\n")
          f.write(f"    toplevel_lang = \"verilog\",\n")
          f.write(f"    toplevel = \"{obj.object_name}\",\n")
          f.write(f"    module = \"{target_test_file}\",\n")
          f.write(f"    timescale = \"1ns/1ps\"\n")
          f.write(f"  )\n")
          f.write(f"  pass\n")
          f.write(f"\n")
          f.write(f"\n")
          f.write(f"@cocotb.test()\n")
          f.write(f"async def cocotb_{target_test_file}(dut):\n")
          f.write(f"  await _{test.test}(dut)\n")
          f.write(f"  pass\n")
          test_id += 1
    subprocess.run(["pytest","out/cocotb_test"],cwd=workspace_dir)
    pass

def clean():
   import shutil
   dir = workspace_dir/"out"/"cocotb_test"
   if dir.exists():
      shutil.rmtree(dir)
   else:
      dir.mkdir()


if __name__ == '__main__':
  require_version((3, 12))
  clean()
  with open("cocotb_test.toml", "rb") as f:
    config = tomllib.load(f)
    tests = config["tests"]
    objs = []
    for test in tests:
      if isinstance(test, dict) == False:
        continue
      if test.get("disable") == True:
        continue
      obj = EmitVerilogObject(test["package"],test["object"])
      params = test["params"]
      # print(params)
      for param in params:
        # print(param)
        cocotb_tests = CocotbTest(test["test"],param)
        obj.add_cocotb_test(cocotb_tests)
      objs.append(obj)
    emitVerilog(objs)
    buildCototbTest(objs)
  
  