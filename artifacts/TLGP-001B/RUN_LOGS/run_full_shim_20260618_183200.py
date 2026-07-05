import pathlib
import runpy
import sys
import types


repo = pathlib.Path.cwd()
src_module = types.ModuleType("src")
src_module.__path__ = [str(repo / "src")]
sys.modules["src"] = src_module
sys.argv = ["src.tlgp_001b.harness", "--full"]
runpy.run_module("src.tlgp_001b.harness", run_name="__main__", alter_sys=True)
