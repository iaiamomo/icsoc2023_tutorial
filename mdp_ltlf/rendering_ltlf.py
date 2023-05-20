from typing import Callable

from graphviz import Digraph
from mdp_dp_rl.processes.mdp import MDP

from mdp.types import State, Action


def mdp_ltlf_to_graphviz(
    mdp: MDP,
    state2str: Callable[[State], str] = lambda x: str(x),
    action2str: Callable[[Action], str] = lambda x: str(x),
    no_sink: bool = False,
) -> Digraph:
    """
    Translate a composition-MDP instance into a Digraph.
    :param mdp: the composition-MDP object, obtained from composition.composition_mdp
    :param state2str: a callable that transforms states into strings
    :param action2str: a callable that transforms actions into strings
    :param no_sink: don't print terminal states.
    :return: the graphviz.Digraph object
    """
    graph = Digraph(format="svg")
    graph.node("fake", style="invisible")
    graph.attr(rankdir="LR")

    ignore_states = set() if not no_sink else mdp.get_sink_states()

    for state in mdp.all_states:
        if state in ignore_states:
            continue
        shape = "doubleoctagon" if state in mdp.get_terminal_states() else "box"
        if state == mdp.initial_state:
            graph.node(state2str(state), root="true", shape=shape)
        else:
            graph.node(state2str(state), shape=shape)

    if mdp.initial_state in mdp.all_states:
        graph.edge("fake", state2str(mdp.initial_state), style="bold")

    for start, outgoing in mdp.transitions.items():
        for action, next_states in outgoing.items():
            reward = mdp.rewards.get(start, {}).get(action, 0.0)
            for end, prob in next_states.items():
                if end in ignore_states:
                    continue
                label = f"{action2str(action)},{reward},{prob}"
                graph.edge(
                    state2str(start),
                    state2str(end),
                    label=label,
                )

    return graph
