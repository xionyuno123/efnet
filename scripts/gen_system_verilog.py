import pathlib
import argparse
import sys
import subprocess
import json

class ChiselModule():
  name:str
  target_dir:pathlib.Path
  params:dict

  def __init__(self,name:str,target_dir:pathlib.Path,params:dict):
    self.name = name
    self.target_dir = target_dir
    self.params = params
  
  def __format__(self, format_spec: str) -> str:
    paramstr = ""
    for key in self.params.keys():
      paramstr += f"{key} = {self.params[key]},"
    if paramstr != "":
      paramstr = paramstr[:-1]

    return f"circt.stage.ChiselStage.emitSystemVerilogFile(new {self.name}({paramstr}),Array(\"--target-dir\",\"{self.target_dir}\"))"


class SVGenerator():
  modules: list[ChiselModule]
  source_dir: pathlib.Path

  def __init__(self,source_dir:pathlib.Path,modules:list[ChiselModule]):
    self.modules = modules
    self.source_dir = source_dir

  def gen(self,mill_object:str):
    with open(self.source_dir/"src/main/scala/main.scala","w") as f:
      f.write("package main\n")
      f.write("import chisel3._\n")
      f.write("object Main extends App {\n")
      for module in self.modules:
        f.write(f"{module}\n")
      f.write("}\n")
    
    cmd = subprocess.run(["mill",f"{mill_object}.run"],cwd=self.source_dir)
    if cmd.returncode != 0:
      raise f"Failed to execute `mill {mill_object}.run` at {self.source_dir}"
      