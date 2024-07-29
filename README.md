# Finite State Machines
Display, run, and minimize deterministic finite state machines, aka finite automata.


## Installation

Simply download [fsm.py](fsm.py) and install the graphviz python package.

You can also clone this repository to get the [example files](example_files/) as well.

## Usage
```
python3 fsm.py [-h] [-i INPUTSTRING] [-d] [-D] fsmfile
```
Use
```
python3 fsm.py --help
```
for a more detailed explanation.

## Syntax of the fsm-files
Each line defines a state with all transitions starting from it. For example,
```
+foo: a -> bar; b,c -> baz; d -> foo; * -> qux
```
defines the accepting (+) state called `foo`, which has a transition to the state `bar` on character "a", transitions to `baz` on "b" or "c", one to itself on "d", and a wildcard (`*`) to `qux`, i.e. any other character transitions to qux.
- Lines must start with either '+' (accepting) or '-' (rejecting).
- The first line defines the initial state.
- The rejecting state `_undefined_` is implicitly defined if any transition is undefined. Every transition from `_undefined_` leads back to itself.
- Invalid characters for state names and input characters are tabs, spaces, `+`, `-`, `>`, `;`, `:`, and `,`.
- This tool does not support non-deterministic automata (yet), so there must not be multiple transitions for a single character within a line.
- A wildcard may only be used in the very last transition of a line, where it defines a transition for all characters for which no transition was defined before.
- Comments start with `//`. Everything after `//` until the end of the line is ignored.
- Tabs and spaces are ignored.
