import asyncio
from typing import List
from pathlib import Path
import json

from mdp_dp_rl.processes.det_policy import DetPolicy
from aida.lmdp import LMDP

from aida.constants import GAMMAS
from aida.lvi import lexicographic_value_iteration
from IndustrialAPI.run_target_lmdp_ltlf import target_dfa, TargetDFA

from IndustrialAPI.actors_api_lmdp_ltlf.client_wrapper import ClientWrapper
from IndustrialAPI.actors_api_lmdp_ltlf.data import ServiceInstance
from IndustrialAPI.actors_api_lmdp_ltlf.helpers import setup_logger
from aida.lmdp import compute_composition_lmdp

logger = setup_logger("orchestrator")

mode = "lmdp_ltlf"

file_plan = "plan.txt"

async def main(host: str, port: int) -> None:
    client = ClientWrapper(host, port)

    # check health
    response = await client.get_health()
    assert response.status_code == 200

    # get all services
    services: List[ServiceInstance] = await client.get_services()
    services = sorted(services, key=lambda x: x.service_id)
    logger.info(f"Got {len(services)} available services")

    # start main loop
    old_policy = None

    # target file
    dfa_target = target_dfa(Path(f"IndustrialAPI/actors_api_{mode}/descriptions/target.tdl"))
    target_simulator = TargetDFA(dfa_target)
    
    system_state = [service.current_state for service in services]
    iteration = 0
    
    lmdp: LMDP = compute_composition_lmdp(dfa_target, [service.current_service_spec for service in services], GAMMAS)
    # set tolerance to stop value iteration earlier for faster convergence
    result_vf, actions = lexicographic_value_iteration(lmdp, tol=1e-5)
    orchestrator_policy = DetPolicy({s: list(opt_actions_from_s)[0] for s, opt_actions_from_s in actions.items()})
    old_policy = orchestrator_policy

    with open(file_plan, "w+") as f:
        f.write("")
    
    while True:        

        # detect when policy changes
        if old_policy.policy_data != orchestrator_policy.policy_data:
            logger.info(f"Optimal Policy has changed!\nold_policy = {old_policy}\nnew_policy={orchestrator_policy}")
        old_policy = orchestrator_policy

        # waiting for target action
        logger.info("Waiting for messages from target...")
        current_target_state = target_simulator.current_state

        logger.info(f"Iteration: {iteration}")
        current_state = (tuple(system_state), current_target_state)
        logger.info(f"Current state (system_state, target_state): {current_state}")

        orchestrator_choice = orchestrator_policy.get_action_for_state(current_state)
        if orchestrator_choice == "undefined":
            logger.error(f"Execution failed: composition failed in system state {system_state}")
            break
        
        # send_action_to_service
        target_action, service_index = orchestrator_choice
        logger.info(f"Chosen service: {service_index}, chosen action: {target_action}")
        
        service = services[service_index]
        service_id = service.service_id
        old_transition_function = service.transition_function

        logger.info(f"Sending message to thing: {service_id}, {target_action}")
        input("Press Enter to continue...")

        # rompere il servizio
        #logger.info(f"Breaking service {service_id}")
        #service = services[service_index]
        #service.current_state = "broken"
        #await client.break_service(service_id)

        with open(file_plan, "a") as f:
            f.write(f"{service_id}:{target_action}:{service.current_state}\n")

        input("Press Enter to continue..., check if service is broken")
        response = await client.execute_service_action(service_id, target_action)
        if response.status_code != 200:
            logger.error(f"Execution failed: composition failed in system state {system_state} cause {service_id} is broken")
            system_state[service_index] = "broken"
            logger.info("Sleeping one second...")
            await asyncio.sleep(1.0)
            continue

        logger.info(f"Action has been executed")
        # take new service instance state with the action executed
        new_service_instance = await client.get_service(service_id)
        
        if old_transition_function != new_service_instance.transition_function:
            logger.info(f"Transition function for service {new_service_instance.service_id} has changed! Old: {services[service_index].transition_function}, New: {new_service_instance.transition_function}")
            lmdp: LMDP = compute_composition_lmdp(dfa_target, [service.current_service_spec for service in services], GAMMAS)
            # set tolerance to stop value iteration earlier for faster convergence
            result_vf, actions = lexicographic_value_iteration(lmdp, tol=1e-5)
            orchestrator_policy = DetPolicy({s: list(opt_actions_from_s)[0] for s, opt_actions_from_s in actions.items()})
            old_policy = orchestrator_policy

        with open(file_plan, "a") as f:
            f.write(f"\tnew_state:{new_service_instance.current_state}\n")
        
        services[service_index] = new_service_instance
        system_state[service_index] = new_service_instance.current_state

        if target_action in dfa_target.alphabet:
            target_simulator.update_state(target_action)

        if target_simulator.current_state in dfa_target.accepting_states:
           logger.info(f"Target has reached accepting state {target_simulator.current_state}, stopping execution")
           return

        logger.info(f"Next service state: {new_service_instance.current_state}")
        #old_transition_function = services[service_index].transition_function
        if old_transition_function != new_service_instance.transition_function:
            logger.info(f"Transition function has changed!\nOld: {old_transition_function}\nNew: {new_service_instance.transition_function}")

        input("Press Enter to continue...")

        logger.info("Sleeping one second...")
        await asyncio.sleep(1.0)
        iteration += 1


if __name__ == "__main__":
    result = asyncio.get_event_loop().run_until_complete(main("localhost", 8080))
