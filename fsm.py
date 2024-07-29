#!/usr/bin/env python3

import argparse
import os
import sys
from graphviz import Source


UNDEFINED = "_undefined_"
WILDCARD_NOTATION = "*" # whats written in the fsm file as a wildcard
WILDCARD = 42 # non-string value without meaning. This is used in the hash maps
ARGPARSE_EPILOG = """
Author & License
  Written by Samsu-F, 2024.
  github.com/Samsu-F
  This software is distributed under the GNU General Public License v3.0.
""" # TODO: add explanation for fsm file syntax



class Fsm:
    def __init__(self, fsmfilename, alphabet=None):
        self.states = {}
        self.state_accepting = {}
        self.initial_state = None
        with open(fsmfilename, "r") as file:
            lines = file.read().splitlines()
            for line_number, line in enumerate(lines):
                line = line.split("//")[0]  # remove comments
                line = ''.join(c for c in line if c not in " \t")   # remove tabs and spaces
                if line == '':
                    continue    # skip empty lines
                assert line[0] in ("+", "-")
                accepting = (line[0] == "+")
                line = line[1:] # remove first char
                split = line.split(":")
                assert len(split) == 2
                state_name, transitions = split
                if self.initial_state is None:
                    self.initial_state = state_name     # first line is initial state
                self.states[state_name] = {}
                self.state_accepting[state_name] = accepting
                transitions = transitions.split(";")
                defined_chars = set()
                wildcard_used = False
                for t in transitions:
                    if t == '':
                        continue
                    split = t.split("->")
                    assert len(split) == 2
                    destination_state = split[1]
                    char_list = split[0].split(",")
                    for c in char_list:
                        if wildcard_used:
                            sys.exit(f"Invalid fsmfile {fsmfilename}: transitions defined after wildcard transition in line {line_number+1}.")
                        if c == WILDCARD_NOTATION:
                            # if wildcard_used:
                            #     sys.exit(f"Invalid fsmfile {fsmfilename}: multiple wildcards in line {line_number}.")
                            wildcard_used = True
                            if alphabet is None:
                                self.states[state_name][WILDCARD] = destination_state
                            else:
                                for c in alphabet:
                                    if c not in defined_chars:
                                        self.states[state_name][c] = destination_state
                                        defined_chars.add(c)
                        else:
                            if c in defined_chars:
                                sys.exit(f"Invalid fsmfile {fsmfilename}: multiple transitions defined for character '{c}' in line {line_number+1}.")
                            self.states[state_name][c] = destination_state
                            defined_chars.add(c)
        self.current_state = self.initial_state



    # transform self into the equivalent minimal DFA 
    def minimize(self):
        marked = True    # constants to make the code more readable
        unmarked = False

        # remove unreachable states
        visited = set()
        queue = set([self.initial_state])
        while len(queue) > 0:
            s = queue.pop()
            visited.add(s)
            for t in self.states[s].values():
                if t not in visited:
                    queue.add(t)
        state_list = list(visited)
        equiv_table = {}
        # initialize
        for i_s, s in enumerate(state_list):
            equiv_table[s] = {}
            for t in state_list[i_s+1:]:
                if self.state_accepting[s] != self.state_accepting[t]:
                    equiv_table[s][t] = marked
                else:
                    equiv_table[s][t] = unmarked

        changed = -1
        loop = 0    # debugging
        while changed != 0:
            print(f"{loop=}, {changed=}", file=sys.stderr)
            loop += 1
            changed = 0
            for i_s, s in enumerate(state_list):
                for t in state_list[i_s+1:]:
                    if equiv_table[s][t] == marked:
                        continue
                    transition_chars = set(self.states[s]).union(set(self.states[t]))
                    for c in transition_chars:
                        try:
                            q = self.states[s][c]
                            r = self.states[t][c]
                        except:
                            sys.exit(f"Error: Minimization is not supported for partially defined transition functions.\nOnly one of the states {s} and {t} has a transition for character '{c}'.\nYou may need the --alphabet option if wildcards are used in the definition.")
                        if q == r:
                            continue
                        if state_list.index(q) > state_list.index(r):
                            q, r = r, q
                        if equiv_table[q][r] == marked:
                            equiv_table[s][t] = marked
                            changed += 1
                            break
        print("finished minimization main loop", file=sys.stderr)

        # build new automaton
        replaced = {}   # (replaced[x] == y) means x was replaced by y
        for i_s, s in enumerate(state_list):
            for t in state_list[i_s+1:]:
                if equiv_table[s][t] == unmarked:
                    # s and t are equivalent
                    while s in replaced:
                        s = replaced[s]
                    assert t != s
                    replaced[t] = s

        new_states = {}
        new_accepting = {}
        for s in state_list:
            if s not in replaced:
                replaced[s] = s
                new_states[s] = {}
                new_accepting[s] = self.state_accepting[s]
        for s in state_list:
            assert replaced[s] in new_states
            for c in self.states[s]:
                new_states[replaced[s]][c] = replaced[self.states[s][c]]

        self.states = new_states
        self.state_accepting = new_accepting
        self.initial_state = replaced[self.initial_state]
        print(f"finished minimization, minimal automaton has {len(new_states)} states.", file=sys.stderr)



    def single_transition(self, input_char):
        assert len(input_char) == 1
        transitions = self.states[self.current_state]
        if input_char in transitions:
            self.current_state = transitions[input_char]
            return
        elif WILDCARD in transitions:
            self.current_state = transitions[WILDCARD]
            return
        else:
            self.current_state = UNDEFINED
            if UNDEFINED not in self.states:
                self.states[UNDEFINED] = {}
                self.state_accepting[UNDEFINED] = False


    def get_output(self):
        return self.state_accepting[self.current_state]


    def to_dot(self, name="FiniteStateMachine", mark_current_state=False):
        result = f"digraph \"{name}\" {{\n"
        for state in self.states:
            if state == UNDEFINED and not (self.current_state == UNDEFINED and mark_current_state):
                continue
            if self.state_accepting[state]:
                attributes = "shape=doublecircle"
            else:
                attributes = "shape=circle"
            if mark_current_state and state == self.current_state:
                attributes += ", color=red"
            result += f"\t{state} [{attributes}]\n"
        result += f"\t_dummy_for_initial_state_ [shape=point, width=0, style=invis] // A dummy node used to for the initial state arrow\n"
        result += f"\t_dummy_for_initial_state_ -> {self.initial_state}\n"
        for state in self.states:
            if state == UNDEFINED:
                continue
            for char, next_state in self.states[state].items():
                if char == WILDCARD:
                    char = WILDCARD_NOTATION
                result += f"\t{state} -> {next_state} [label=\"{char}\"]\n"
        result += "}"
        return result


    def display(self, mark_current_state=False, name="FiniteStateMachine", format="png", suppress_error=True):
        graph = Source(self.to_dot(name=name, mark_current_state=mark_current_state))
        graph.render(view=True, filename=f"/tmp/{name}.gv", format=format, quiet_view=suppress_error)




def parse_args() -> argparse.ArgumentParser:
    argparser = argparse.ArgumentParser(
                    # prog='fsm'
                    # usage='%(prog)s [options] fsmfile',
                    description='A Finite State Machine Interpreter',
                    formatter_class=argparse.RawDescriptionHelpFormatter,
                    epilog=ARGPARSE_EPILOG
                    )
    argparser.add_argument('fsmfile', type=str,
                                help="""The file containing the finite state machine to simulate""")  # mandatory positional argument
    argparser.add_argument('-i', '--inputstring', required=False, type=str, default=None,
                                help="""The string that serves as an input for the finite state machine.
                                        Run the finite state machine on this string and print whether it accepts or rejects it.""")
    argparser.add_argument('-d', '--display_initial', required=False, dest='display_initial', default=False, action='store_true',
                                help="Display the initial state of the fsm.")
    argparser.add_argument('-D', '--display_final', required=False, dest='display_final', default=False, action='store_true',
                                help="Display the final state of the fsm, final state will be marked in red.")
    argparser.add_argument('-m', '--minimize', required=False, dest='minimize', default=False, action='store_true',
                                help="Minimize the fsm before anything else. This option is only supported for fully defined automata. If wildcards are used, the --alphabet option is mandatory.")
    argparser.add_argument('-a', '--alphabet', required=False, type=str, default=None,
                                help="""Define the alphabet, i.e. the meaning of the wildcard as a comma-separated list.
                                        For example, -a 'a, b, c'.""")

    args = argparser.parse_args()
    if args.display_final and args.inputstring is None:
        argparser.error('-i/--inputstring is mandatory when -D/--display_initial is used')
    if not args.display_initial and not args.display_final and args.inputstring is None:
        argparser.error('At least one of the options -i, -d or -D has to be used. Use option -h for help.')
    return args




def main():
    args = parse_args()
    if args.alphabet is not None:
        args.alphabet = set(args.alphabet.split(','))

    fsm = Fsm(args.fsmfile, alphabet=args.alphabet)

    if args.minimize:
        fsm.minimize()

    filename = os.path.basename(args.fsmfile)
    fsmname = filename.rsplit(".fsm", 1)[0]     # remove suffix ".fsm" if it exists

    if args.display_initial:
        fsm.display(name=f"{fsmname}_initial")

    # print(fsm.to_dot(name=fsmname, mark_current_state=True))
    if args.inputstring is not None:
        for char in args.inputstring:
            fsm.single_transition(char)
        if fsm.get_output():
            print(f"The input string \"{args.inputstring}\" is accepted.")
        else:
            print(f"The input string \"{args.inputstring}\" is rejected.")

    if args.display_final:
        fsm.display(mark_current_state=True, name=f"{fsmname}_final")




if __name__ == "__main__":
    main()

