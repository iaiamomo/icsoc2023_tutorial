from local.alto_utils import ALTOUtils
import time
import subprocess
import signal
import os
import asyncio
from alto.actorsAPI import *


app_path = "../IndustrialAPI/actors_api_plan/app.py"
p1 = subprocess.Popen([f"python {app_path}"], shell=True, preexec_fn=os.setsid)

time.sleep(5)

launch_devices_path = "../IndustrialAPI/launch_devices.py"
folder = "../GUI/saved_models/plan_case1"
mode = "plan"
p2 = subprocess.Popen([f"python {launch_devices_path} {folder} {mode}"], shell=True)

alto = ALTOUtils("../GUI/saved_models/plan_case1/target.tdl")

time.sleep(3)

while True:
    res = asyncio.get_event_loop().run_until_complete(alto.compute_plan())

    print(res)
    
    input()

print("Stopping...")
os.killpg(os.getpgid(p1.pid), signal.SIGTERM)
