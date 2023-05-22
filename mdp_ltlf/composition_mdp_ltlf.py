from collections import deque
from typing import Sequence, Deque

from mdp_dp_rl.processes.mdp import MDP
from pythomata import SimpleDFA

from utils.services import Service, build_system_service
from utils.types import MDPDynamics

COMPOSITION_MDP_INITIAL_STATE = 0
COMPOSITION_MDP_INITIAL_ACTION = "initial"
COMPOSITION_MDP_UNDEFINED_ACTION = "undefined"
DEFAULT_GAMMA = 0.9

COMPOSITION_MDP_SINK_STATE = -1

def composition_mdp_ltlf(
    dfa: SimpleDFA, services: Sequence[Service], gamma: float = DEFAULT_GAMMA
) -> MDP:
    """
    Compute the composition MDP.

    :param target: the target service.
    :param services: the community of services.
    :param gamma: the discount factor.
    :return: the composition MDP.
    """
    dfa = dfa.trim()
    #print("Start build system service ", time.time_ns())
    system_service = build_system_service(*services)
    #print("Stop build system service", time.time_ns())

    transition_function: MDPDynamics = {}

    visited = set()
    to_be_visited = set()
    queue: Deque = deque()

    # add initial transitions
    initial_state = (system_service.initial_state, dfa.initial_state)
    queue.append(initial_state)
    to_be_visited.add(initial_state)
    for system_service_state in system_service.states:
        if system_service_state == system_service.initial_state:
            continue
        new_initial_state = (system_service_state, dfa.initial_state)
        queue.append(new_initial_state)
        to_be_visited.add(new_initial_state)

    service_id_to_target_action = {
        service_id: set(dfa.alphabet).intersection(service.actions)
        for service_id, service in enumerate(services)
    }
    target_action_to_service_id = {}
    for service_id, supported_actions in service_id_to_target_action.items():
        assert len(supported_actions) == 1
        supported_action = list(supported_actions)[0]
        target_action_to_service_id.setdefault(supported_action, set()).add(service_id)

    mdp_sink_state_used = False
    while len(queue) > 0:
        cur_state = queue.popleft()
        to_be_visited.remove(cur_state)
        visited.add(cur_state)
        cur_system_state, cur_dfa_state = cur_state
        trans_dist = {}

        next_system_state_trans = system_service.transition_function[
            cur_system_state
        ].items()

        # optimization: filter services, consider only the ones that can do the next DFA action
        next_dfa_actions = set(dfa.transition_function.get(cur_dfa_state, {}).keys())
        allowed_services = set()
        for next_dfa_action in next_dfa_actions:
            allowed_services.update(target_action_to_service_id[next_dfa_action])

        if len(allowed_services) == 0:
            mdp_sink_state_used = True
            trans_dist[COMPOSITION_MDP_UNDEFINED_ACTION] = ({COMPOSITION_MDP_SINK_STATE: 1}, 0.0)
        else:
            # iterate over all available actions of system service
            # in case symbol is in DFA available actions, progress DFA state component
            for (symbol, service_id), next_state_info in next_system_state_trans:

                if service_id not in allowed_services:
                    # this service id cannot do any of the next dfa actions
                    continue

                next_system_state_distr, reward_vector = next_state_info
                system_reward = reward_vector

                # if symbol is a tau action, next dfa state remains the same
                if symbol not in dfa.alphabet:
                    next_dfa_state = cur_dfa_state
                    goal_reward = 0.0
                # if there are no outgoing transitions from DFA state:
                elif cur_dfa_state not in dfa.transition_function:
                    mdp_sink_state_used = True
                    trans_dist[COMPOSITION_MDP_UNDEFINED_ACTION] = ({COMPOSITION_MDP_SINK_STATE: 1}, 0.0)
                    continue
                # symbols not in the transition function of the target
                # are considered as "other"; however, when we add the
                # MDP transition, we will label it with the original
                # symbol.
                elif symbol in dfa.transition_function[cur_dfa_state]:
                    symbol_to_next_dfa_states = dfa.transition_function[cur_dfa_state]
                    next_dfa_state = symbol_to_next_dfa_states[symbol]
                    goal_reward = 1.0 if dfa.is_accepting(next_dfa_state) else 0.0
                else:
                    # if invalid target action, skip
                    continue
                final_rewards = (goal_reward + system_reward)

                for next_system_state, prob in next_system_state_distr.items():
                    assert prob > 0.0
                    next_state = (next_system_state, next_dfa_state)
                    trans_dist.setdefault((symbol, service_id), ({}, final_rewards))[0][
                        next_state
                    ] = prob
                    if next_state not in visited and next_state not in to_be_visited:
                        queue.append(next_state)
                        to_be_visited.add(next_state)

        transition_function[cur_state] = trans_dist

    if mdp_sink_state_used:
        transition_function[COMPOSITION_MDP_SINK_STATE] = {COMPOSITION_MDP_UNDEFINED_ACTION: ({COMPOSITION_MDP_SINK_STATE: 1.0}, 0.0)}

    result = MDP(transition_function, gamma)
    result.initial_state = initial_state
    return result
