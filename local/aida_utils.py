#!/usr/bin/env python3
from typing import List
from pathlib import Path

from mdp_dp_rl.processes.det_policy import DetPolicy
from aida.lmdp import LMDP

from aida.constants import GAMMAS
from aida.lvi import lexicographic_value_iteration
from IndustrialAPI.run_target_lmdp_ltlf import target_dfa, TargetDFA

from IndustrialAPI.actors_api_lmdp_ltlf.client_wrapper import ClientWrapper
from IndustrialAPI.actors_api_lmdp_ltlf.data import ServiceInstance
from aida.lmdp import compute_composition_lmdp


class AIDAUtils:

    def __init__(self, dfa_path):
        self.client = ClientWrapper("localhost", 8080)

        self.dfa_path = dfa_path
        self.dfa_target = None
        self.target_simulator = None
        #print(self.dfa_target.alphabet.symbols)
        self.set_targetDFA()

        self.policy : DetPolicy = None

    def set_targetDFA(self):
        self.dfa_target = target_dfa(Path(self.dfa_path))
        self.target_simulator = TargetDFA(self.dfa_target)

    async def get_services(self):
        services: List[ServiceInstance] = await self.client.get_services()
        services = sorted(services, key=lambda x: x.service_id)
        return services
    
    async def compute_policy(self):
        services = await self.get_services()
        lmdp: LMDP = compute_composition_lmdp(self.dfa_target, [service.current_service_spec for service in services], GAMMAS)
        # set tolerance to stop value iteration earlier for faster convergence
        result_vf, actions = lexicographic_value_iteration(lmdp, tol=1e-5)
        self.policy = DetPolicy({s: list(opt_actions_from_s)[0] for s, opt_actions_from_s in actions.items()})

    async def get_current_system_state(self):
        services = await self.get_services()
        return [service.current_state for service in services]
    
    async def get_current_state(self):
        system_state = await self.get_current_system_state()
        return (tuple(system_state), self.target_simulator.current_state)
    
    async def get_action(self):
        current_state = await self.get_current_state()
        print(current_state)
        target_action, service_index = self.policy.get_action_for_state(current_state)
        return [target_action, service_index]
    
    async def execute_action(self, service_index, target_action):
        services = await self.get_services()
        service = services[service_index]
        service_id = service.service_id
        old_transition_function = service.transition_function
        current_state = service.current_state
        await self.client.execute_service_action(service_id, target_action)
        updated_service = await self.client.get_service(service_id)
        new_state = updated_service.current_state
        new_transition_function = updated_service.transition_function
        if old_transition_function != new_transition_function:
            print("transition function diversa")
            return service_id, current_state, new_state, 0 # return 0 if the lmdp needs to be recomputed
        else:
            print("transition function uguale")
            return service_id, current_state, new_state, 1
            
    async def next_step(self):
        target_action, service_index = await self.get_action()
        print(target_action)
        service_id, current_state, new_state, recompute = await self.execute_action(service_index, target_action)
        self.update_dfa_target(target_action)
        if recompute == 0:
            await self.recompute_lmdp()
        if await self.check_execution_finished():
            self.set_targetDFA()
            return service_id, current_state, new_state, target_action, True
        return service_id, current_state, new_state, target_action, False
        
    def update_dfa_target(self, target_action):
        if target_action in self.dfa_target.alphabet:
            self.target_simulator.update_state(target_action)

    def stop_execution(self):
        if self.target_simulator.current_state in self.dfa_target.accepting_states:
            return True
        return False
    
    async def recompute_lmdp(self):
        await self.compute_policy()


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
    

    async def service_current_status(self, service_id):
        service = await self.client.get_service(service_id)
        return service.current_state
    
    
    async def break_service(self, service_id):
        await self.client.break_next_service(service_id)


    def change_probabilities(self, n_runs):
        services : List[ServiceInstance] = self.get_services()
        for service in services:
            print()
            # update probabilities through client