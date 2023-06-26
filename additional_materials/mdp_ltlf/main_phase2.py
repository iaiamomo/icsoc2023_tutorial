import argparse
import asyncio
from pathlib import Path
from typing import List

from mdp_dp_rl.processes.mdp import MDP

from OLDIndustrialAPI.run_target_mdp_ltlf import target_dfa, TargetDFA

from OLDIndustrialAPI.actors_api_mdp_ltlf.client_wrapper import ClientWrapper
from OLDIndustrialAPI.actors_api_mdp_ltlf.data import ServiceInstance, TargetInstance, ServiceId
from OLDIndustrialAPI.actors_api_mdp_ltlf.helpers import setup_logger
from mdp_ltlf.composition_mdp_ltlf import composition_mdp_ltlf

logger = setup_logger("orchestrator")

mode = "mdp_ltlf"

parser = argparse.ArgumentParser("main")
parser.add_argument("--host", type=str, default="localhost", help="IP address of the HTTP IoT service.")
parser.add_argument("--port", type=int, default=8080, help="IP address of the HTTP IoT service.")


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
    dfa_target = target_dfa(Path(f"IndustrialAPI/actors_api_{mode}/descriptions_phase2/target_phase2.tdl"))
    target_simulator = TargetDFA(dfa_target)

    system_state = [service.service_spec.initial_state for service in services]
    iteration = 0

    while True:

        mdp: MDP = composition_mdp_ltlf(dfa_target, [service.current_service_spec for service in services])
        orchestrator_policy = mdp.get_optimal_policy()

        # detect when policy changes
        if old_policy is None:
            old_policy = orchestrator_policy
        if old_policy.policy_data != orchestrator_policy.policy_data:
            logger.info(f"Optimal Policy has changed!\nold_policy = {old_policy}\nnew_policy={orchestrator_policy}")
        old_policy = orchestrator_policy

        # waiting for target action
        logger.info("Waiting for messages from target...")
        current_target_state = target_simulator.current_state

        logger.info(f"Iteration: {iteration}")
        current_state = (tuple(system_state), current_target_state)
        logger.info(f"Current state: {current_state}")

        orchestrator_choice = orchestrator_policy.get_action_for_state(current_state)
        if orchestrator_choice == "undefined":
            logger.error(f"Execution failed: composition failed in system state {system_state}")
            break
        # send_action_to_service
        target_action, service_index = orchestrator_choice
        logger.info(f"Chosen service: {service_index}, chosen action: {target_action}")
        service_id = services[service_index].service_id
        logger.info(f"Sending message to thing: {service_id}, {target_action}")
        await client.execute_service_action(service_id, target_action)
        logger.info(f"Action has been executed")
        new_service_instance = await client.get_service(service_id)
        if services[service_index].transition_function != new_service_instance.transition_function:
            logger.info(f"Transition function for service {new_service_instance.service_id} has changed! Old: {services[service_index].transition_function}, New: {new_service_instance.transition_function}")
        services[service_index] = new_service_instance
        system_state[service_index] = new_service_instance.current_state
        target_simulator.update_state(target_action)
        if target_simulator.current_state in target_dfa.accepting_states:
           target_simulator.reset()

        logger.info(f"Next service state: {new_service_instance.current_state}")
        old_transition_function = services[service_index].transition_function
        if old_transition_function != new_service_instance.transition_function:
            logger.info(f"Transition function has changed!\nOld: {old_transition_function}\nNew: {new_service_instance.transition_function}")

        logger.info("Sleeping one second...")
        await asyncio.sleep(1.0)
        iteration += 1


if __name__ == "__main__":
    arguments = parser.parse_args()
    result = asyncio.get_event_loop().run_until_complete(main(arguments.host, arguments.port))
