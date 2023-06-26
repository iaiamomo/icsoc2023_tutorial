#!/usr/bin/env python3
from typing import List
from pathlib import Path

from alto.buildPDDL import *
from alto.config import *
from alto.actorsAPI import *

from IndustrialAPI.actors_api_plan.client_wrapper import ClientWrapper

import subprocess


class ALTOUtils:

    def __init__(self, target):
        self.target = target
        self.desc : Description = None
        self.plan = None
        self.plan_step = 0

        self.domain = f"{config.PDDL['domainName']}.pddl"
        self.problem = f"{config.PDDL['problemName']}.pddl"

        self.plan_file = config.PDDL['planFile']

        self.client = ClientWrapper("localhost", 8080)


    async def getServices(self):
        services = await self.client.get_services()
        return services


    async def set_desc(self):
        services = await self.getServices()
        self.desc = buildPDDL(services, self.domain, self.problem, self.target)


    async def compute_plan(self):
        await self.set_desc()
        command = f"./alto/downward/fast-downward.py {self.domain} {self.problem} --search 'astar(lmcut())'" 
        result = subprocess.run(command, shell = True, stdout=subprocess.PIPE)
        print(f"Result planner: {result.returncode}")
        if result.returncode > 9:
            return -1

        plan = []
        with open(config.PDDL['planFile']) as file_in:
            for line in file_in:
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

    
    def get_next_action(self):
        if self.plan_step >= len(self.plan):
            return None
        
        action = json.load(self.plan[self.plan_step])
        return action


    async def next_step(self):
        action = self.get_next_action()

        serviceId = action["service_id"]
        cmd = action["command"]
        params = action["parameters"]
        expected = self.desc.getGroundedEffect(cmd, params)

        response = await self.client.execute_service_action(serviceId, action)
        event = json.loads(response.content)
        value = event["value"]
        output = event["output"]
        cost = event["cost"]

        if value == "terminated":
            return 0, action
        
        if output != expected:
            return -1, action
        
        return 1, action
        
    
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
        await self.client.break_service(serviceId)

