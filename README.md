# Finite State Machines
Display and run (deterministic) finite state machines, aka finite automata.


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
+foo: a -> bar; b,c -> baz; d -> foo
```
defines the accepting (+) state called `foo`, which has a transition to the state `bar` on character "a", transitions to `baz` on "b" or "c", and one to itself on "d".
Lines must start with either '+' (accepting) or '-' (rejecting).
The first line defines the initial state.
The non-accepting state `_undefined_` is implicitly defined if any transition is undefined. Every transition from `_undefined_` leads back to itself.
Invalid characters for state names and input characters are tabs, spaces, `+`, `-`, `>`, `;`, `:`, `;` and `,`.
