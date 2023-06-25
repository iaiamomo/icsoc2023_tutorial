import asyncio
import json
import alto.config
import subprocess
from alto.buildPDDL import *
from alto.config import *
import requests
from alto.actorsAPI import *

import cProfile
import pstats
import io
import time

rnd = 0
total_cost = 0

config_json = json.load(open('config.json', 'r'))
mode = config_json['mode']
phase = config_json['phase']
size = config_json['size']

def execute_downward(domain, problem):
    command = f"./downward/fast-downward.py {domain} {problem} --search 'astar(lmcut())'" 
    result = subprocess.run(command, shell = True, stdout=subprocess.PIPE)
    return result

async def executionEngine(rnd, tot_cost):
    if phase == 1:
        domain = f"{config.PDDL['domainName']}_phase{phase}.pddl"
        problem = f"{config.PDDL['problemName']}_phase{phase}.pddl"
    elif phase == 2:
        domain = f"{config.PDDL['domainName']}_phase{phase}_{size}.pddl"
        problem = f"{config.PDDL['problemName']}_phase{phase}_{size}.pddl"
    else:
        domain = f"{config.PDDL['domainName']}.pddl"
        problem = f"{config.PDDL['problemName']}.pddl"

    # Retrieve information of Things and construct PDDL domain and problem files
    print("Collecting problem data...")
    desc = buildPDDL(phase, domain, problem)

    #input("press enter to continue...")
    
    # Call planner
    # If plan not found, return 2 
    print("Invoking planner...")

    now = time.time_ns()
    result = execute_downward(domain, problem)
    elapsed = time.time_ns() - now
    print(f"elapsed time: {elapsed} ns")
    if phase == 1:
        file_name = f'profiling_phase{phase}.txt'
    elif phase == 2:
        file_name = f'profiling_phase{phase}_{size}.txt'
    else:
        file_name = f'profiling.txt'
    with open(file_name, 'w+') as f:
        f.write(f"elapsed time: {elapsed} ns\n")
    
    print(f"result planner: {result.returncode}")
    if (result.returncode > 9):
        return [2, tot_cost]
            
    print("Plan found! Proceeding to orchestrate devices...")
    with open(config.PDDL["planFile"]) as file_in:
        for line in file_in:
            if line[0] == ";":
                break
            tokens = line.replace("(","").replace(")","").strip().split(" ")
            serviceId = tokens[1]
            cmd = tokens[0]
            params = []
            for i in range(2, len(tokens)):
                params.append(tokens[i])

            expected = desc.getGroundedEffect(cmd, params)
            print("Issuing command " + tokens[0] +
                    " to " + serviceId + " with parameters " +
                    str(params))
                    
            print("Expected result: " + str(expected))

            body = json.dumps({"command": cmd, "service_id": serviceId, "parameters": params})
            output = None
            while True:
                try:
                    response = sendMessage(serviceId, body)
                except requests.exceptions.Timeout:
                    print("Expired timer! Adapting...")
                    return [1, tot_cost]
                event = json.loads(response.content)
                print(event)
                value = event["value"]
                output = event["output"]
                cost = event["cost"]

                if value == "terminated":
                    break

            print("Received output: " + str(output))
            if output != expected:
                print("Discrepancy detected! Adapting...")
                return [1, tot_cost]
            else:
                tot_cost += cost
                print("total cost: " + str(tot_cost))
            
    return [0, tot_cost]

result, total_cost = asyncio.get_event_loop().run_until_complete(executionEngine(rnd, total_cost))
while result == 1:
    #input("press enter to continue...")
    result, total_cost = asyncio.get_event_loop().run_until_complete(executionEngine(rnd+1, total_cost))

if result == 0:
    print("Success!")
    print("Total cost: " + str(total_cost))
else:
    print("Plan not found!")
                
