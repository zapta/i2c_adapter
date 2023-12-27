# Build the platformio targets and copy their firmware images to ../release.

import subprocess
import os
import re
from typing import List
import shutil
import glob

# TODO: Add command flag for dry run without updating release.
# TODO: Add a command flag for not cleaning before building.
# TODO: Add a command flag build just a single environment
# TODO: Add a command flag for verbose build.

# Path to the platformio command.
pio = os.path.join(os.path.expanduser('~user'), ".platformio/penv/Scripts/pio")


def subprocess_to_list(cmd: str):
    '''
    Return the output of a process to a list of strings. 
    '''
    return subprocess.run(cmd,text=True,stdout=subprocess.PIPE, check=True).stdout.splitlines()
  

def get_platformio_envs()->List[str]:
  """Fetch the list of envs in this platformio project file."""
  print(f"Fetching platformio's environment names.", flush=True)
  lines = subprocess_to_list(f"{pio} run --list-targets")
  pattern = re.compile("^([^\\s]+)[\\s]+Platform[\\s].*$")
  result = []
  for line in lines:
    m = pattern.match(line)
    if m:
      result.append(m.group(1))
  return result
  
# --- Main

"""Clean the envs, build them, and update release directory."""
# Clean platformio builds.
subprocess.run(f"{pio} run --target fullclean", check=True)

# Delete all release files.
for f in glob.glob("../release/*.uf2"):
  os.remove(f)
  
# For each env, built and copy its .uf2 file to release directory.
envs =  get_platformio_envs()
log = []
for env in envs:
  print(f"Building env: {env}",  flush=True)
  subprocess.run(f"{pio} run --environment  {env}", check=True)
  src = f".pio/build/{env}/firmware.uf2"
  dst = f"../release/{env}.uf2"
  shutil.copy(src, dst)
  log.append(f"*  {dst:42} {os.path.getsize(dst):5} Bytes")
  
print(f"\nOutput files:", flush=True)
print("\n".join(log), flush=True)
print( flush=True)

