from local.aida_utils import AIDAUtils
import time
import subprocess
import signal
import os
import asyncio


app_path = "IndustrialAPI/app.py"
p1 = subprocess.Popen([f"python {app_path}"], shell=True, preexec_fn=os.setsid)

time.sleep(5)

launch_devices_path = "IndustrialAPI/launch_devices.py"
p2 = subprocess.Popen([f"python {launch_devices_path}"], shell=True)

aida = AIDAUtils("IndustrialAPI/actors_api_lmdp_ltlf/descriptions/target.tdl")

while True:
    loop = asyncio.get_event_loop().run_until_complete(aida.get_services())
    

    res = aida.stop_execution()
    print(res)

print("Stopping...")
os.killpg(os.getpgid(p1.pid), signal.SIGTERM)
