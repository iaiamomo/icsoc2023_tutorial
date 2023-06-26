import subprocess
import sys
import glob
from typing import List
import json


config_json = json.load(open('../config.json', 'r'))
mode = config_json['mode']
try:
    phase = config_json['phase']
    size = config_json['size']
except Exception as e:
    phase = -1
    size = -1

if __name__ == "__main__":

    processes: List[subprocess.Popen] = []
    
    if phase == 1:
        list_devices = glob.glob(f"actors_api_{mode}/descriptions_phase{phase}/*.json")
    elif phase == 2:
        list_devices = glob.glob(f"actors_api_{mode}/descriptions_phase{phase}/{size}/*.json")
    elif phase == -1 and size == -1:
        list_devices = glob.glob(f"actors_api_{mode}/descriptions/*.sdl")

    for configuration_path in list_devices:
        script = f"run_service_{mode}.py"
        process = subprocess.Popen([sys.executable, script, configuration_path])
        processes.append(process)

    for process in processes:
        process.wait()
