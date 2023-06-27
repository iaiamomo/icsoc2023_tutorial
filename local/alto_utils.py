#!/usr/bin/env python3
from typing import List
from pathlib import Path

from alto.buildPDDL import *
from alto.config import *
from alto.actorsAPI import *

import subprocess


class ALTOUtils:

    def __init__(self, target):
        self.target = target
        self.desc : Description = None
        self.plan = None
        self.plan_step = 0

        self.domain = f"{PDDL['domainName']}.pddl"
        self.problem = f"{PDDL['problemName']}.pddl"

        self.plan_file = PDDL['planFile']


    async def getServices(self):
        services = await searchServices()
        return services


    async def set_desc(self):
        services = await self.getServices()
        self.desc = buildPDDL(services, self.domain, self.problem, self.target)


    async def compute_plan(self):
        await self.set_desc()
        command = f"../alto/downward/fast-downward.py {self.domain} {self.problem} --search 'astar(lmcut())'" 
        result = subprocess.run(command, shell = True, stdout=subprocess.PIPE)
        print(f"Result planner: {result.returncode}")
        if result.returncode > 9:
            return -1

        plan = []
        with open(f"{PDDL['planFile']}") as file_in:
            for line in file_in:
                if ';' in line:
                    continue
                tokens = line.replace("(","").replace(")","").strip().split(" ")
                serviceId = tokens[1]
                cmd = tokens[0]
                params = []
                for i in range(2, len(tokens)):
                    params.append(tokens[i])
                body = json.dumps({"command": cmd, "service_id": serviceId, "parameters": params})
                plan.append(body)

        self.plan = plan
        self.plan_step = 0
        return 1

    
    def get_next_action(self):
        if self.plan_step >= len(self.plan):
            return None
        
        action = self.plan[self.plan_step]
        return action


    async def next_step(self):
        action = self.get_next_action()
        print(action)

        print(type(action))

        json_action = json.loads(action)

        serviceId = json_action["service_id"]
        cmd = json_action["command"]
        params = json_action["parameters"]
        expected = self.desc.getGroundedEffect(cmd, params)

        print(serviceId)
        print(json_action)

        response = await sendMessage(serviceId, json_action)
        event = response
        print(event)
        value = event["value"]
        output = event["output"]
        cost = event["cost"]

        if value == "terminated":
            return 0, json_action
        
        if output != expected:
            return -1, json_action
        
        return 1, json_action
        
    
    async def recompute_plan(self):
        await self.compute_plan()

    
    async def recompute_initial_plan(self):
        #TODO reset services
        await self.compute_plan()


    async def check_execution_finished(self):
        if self.target_simulator.current_state in self.dfa_target.accepting_states:
            target_action, _ = await self.get_action()
            if target_action in self.dfa_target.alphabet:
                next_state = self.target_simulator.next_state(target_action)
                if next_state in self.dfa_target.accepting_states:
                    return False
                else:
                    return True
        return False
    
    
    async def break_service(self, serviceId):
        await breakService(serviceId)

