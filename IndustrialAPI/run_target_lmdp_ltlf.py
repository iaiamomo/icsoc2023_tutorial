# Python imports, put at the top for simplicity
from logaut import ltl2dfa
from pylogics.parsers import parse_ltl
from pythomata import SimpleDFA
from pathlib import Path
import sys
import json

from aida.declare_utils import *
from aida.dfa_target import from_symbolic_automaton_to_declare_automaton, mdp_from_dfa
from IndustrialAPI.utils.utils import render_mdp_dfa



def declare2ltlf(constraint, parameters):
    match constraint:
        case "weak_until":
            assert len(parameters) == 2
            return weak_until(parameters[0], parameters[1])
        case "absence_2":
            assert len(parameters) == 1
            return absence_2(parameters[0])
        case "exactly_once":
            assert len(parameters) == 1
            return exactly_once(parameters[0])
        case "alt_response":
            assert len(parameters) == 2
            return alt_response(parameters[0], parameters[1])
        case "alt_precedence":
            assert len(parameters) == 2
            return alt_precedence(parameters[0], parameters[1])
        case "alt_succession":
            assert len(parameters) == 2
            return alt_succession(parameters[0], parameters[1])
        case "not_coexistence":
            assert len(parameters) == 2
            return not_coexistence(parameters[0], parameters[1])
        

def target_dfa(spec: Path) -> SimpleDFA:
    spec_json = json.load(open(spec))
    data_array = spec_json["target"]
    print(data_array)
    #data_array = spec.read_text().split("\n")
    symbols = set()
    constraints = []

    for data in data_array:
        items = data.replace(" ","").split(":")
        constraint = items[0].strip()
        parameters = items[1].split(",")
        for param in parameters:
            symbols.add(param)
        ltlf_constraint = declare2ltlf(constraint, parameters)
        constraints.append(ltlf_constraint)
    constraints.append(build_declare_assumption(symbols))

    formula_str = " & ".join(map(lambda s: f"({s})", constraints))
    formula = parse_ltl(formula_str)
    automaton = ltl2dfa(formula, backend="lydia")
    declare_automaton = from_symbolic_automaton_to_declare_automaton(automaton, symbols)
    return declare_automaton


class TargetDFA:
    """Simulate a target DFA."""

    def __init__(self, target: SimpleDFA):
        """Initialize the simulator."""
        self.target = target

        self._current_state = self.target.initial_state

    @property
    def current_state(self):
        return self._current_state

    def reset(self):
        """Reset the target to its initial state."""
        self._current_state = self.target.initial_state

    def update_state(self, action) -> None:
        """Update the state given an action."""
        transitions_from_state = self.target.transition_function[self._current_state]
        next_state = transitions_from_state[action]
        self._current_state = next_state

    def next_state(self, action):
        transitions_from_state = self.target.transition_function[self._current_state]
        next_state = transitions_from_state[action]
        print(next_state)
        return next_state

    def update_current_state(self, new_state) -> None:
        self._current_state = new_state


def main(spec):
    """Create target."""
    simple_dfa = simple_dfa(Path(spec))
    target_dfa = TargetDFA(simple_dfa)


if __name__ == "__main__":
    spec = sys.argv[1]
    main(Path(spec))