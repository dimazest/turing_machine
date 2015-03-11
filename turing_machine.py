# -*- coding: utf-8 -*-
"""A Turing machine simulator.

    Accepting '#'
    =============

    >>> from turing_machine import TuringMachine

    Instantiate the machine with particular tranitions.

    >>> one_hash = TuringMachine(
    ...     {
    ...         ('q0', '#'): ('saw_#', '#', 'R'),
    ...         ('saw_#', ''): ('qa', '', 'R'),
    ...     }
    ... )

    Check whether it accepts a string:

    >>> one_hash.accepts('#')
    True

    >>> one_hash.accepts('##')
    False

    Check whether it rejects a string:

    >>> one_hash.rejects('#')
    False

    >>> one_hash.rejects('##')
    True

"""

import logging
from itertools import islice


class TuringMachine:
    """Turing machine with a singly-infinite tape.

    A machine is instantiated with transitions, start, accept and reject states
    and a blank symbol. We assume that the input and the tape alphabet can be
    deducted from the transitions.

    :param dict transitions: a mapping from (state, symbol) tuples to (state,
    symbol, direction) tuple. Note that in theory δ is a transition *function*
    (in the sense of mathematical functions), but we expect a mapping, not a
    callable. Directions are either 'L' (for left) or 'R' (for right).

    :param start_state: the initial state of the machine.

    :param accpet_state: the accept state.

    :param reject_state: the reject state.

    :blank_symbol: the special symbold that marks the tape cell to be empty.

    We don't really care what the input alphabet Σ and the tape alphabet Γ are
    for the purpose of this implementation. For a particular run of the machine,
    the tape alphabet is the union of the input, symbols used in transitions and
    the blank symbol.

    The input on the tape is not part of a Turing machine, so it's not required
    on a Turing  machine instantiation. To execute a particular machine use the
    .run() instance method.

    """

    def __init__(self, transitions, start_state='q0', accept_state='qa', reject_state='qr', blank_symbol=''):
        self.blank_symbol = blank_symbol
        self.transitions = transitions
        self.start_state = start_state
        self.reject_state = reject_state

        self.states_to_actions = {
            accept_state: 'Accept',
            reject_state: 'Reject',
        }

    def run(self, input_):
        """Exectute the Turing machine for a particular input.

        :param input_: the input that is written on the tape. It's can be a list
        of strings. Or just a string, in which case each letter is treated as a
        symbol.

        Given an input a machine can run forever or stop after a number of
        steps. So it would be great if we could write a function that
        potentially runs forever and it's up the the caller to decide how many
        steps are executed. Actually, we should not even bother with this. On
        the other side, ^C is not the best way for a user to tell us to stop.
        Instead we give the user control to execute us one step at a time. This
        is what Python generators are (partially) for. The yield expression
        suspends us and gives controll to the caller until he or she decides to
        resume our execution. Have a look to [1] to get familliar with the yield
        keyord and generators, and hopefully never, ever write something like::

            result = []
            for i in range(len(other_items)):
                item = other_items[i]

                result.append(item * 3)

        At each step the generator yields a (action, configuration) tuple.

        The action is either 'Accept', 'Reject' or None. 'Accept' and `Reject`
        are self explanatory and signal that the input is either accepted or
        rejected the machine stops in these states. None is returned in case the
        machine needs to continue running.

        Configuration is a dictionary with the following keys:
        - 'state' the current state,
        - 'left_hand_side': the symbols on the left hand side of the
          current position.
        - 'symbol': the current symbol,
        - 'right_hand_side': the symbols on the right hand side of the
          current position.

        [1] http://www.jeffknupp.com/blog/2013/04/07/improve-your-python-yield-and-generators-explained/

        """
        state = self.start_state

        # Theory doesn't say how to implement the tape, so we store the symbols
        # on the tape the way that is most suitable for us. We get two lists to
        # store the symbols from left and right hand sides of the current
        # symbol.
        #
        # Initially, there is the blank symbol on the left. Note, that the
        # element at 0 position is the *closest* to the head.
        left_hand_side = [self.blank_symbol]
        if not input_:
            # In case input is empty, pretend that it consists of a blank.
            input_ = [self.blank_symbol]
        # Consume the right most symbol of the input and make it the current
        # symbol, everything else is stored in a list for the right side
        # symbols.
        symbol = input_[0]
        right_hand_side = list(input_[1:])

        while True:
            # Share our state with the caller.
            # Also give them a chance to control our execution.
            action = self.states_to_actions.get(state)
            yield (
                action,
                {
                    'state': state,
                    'left_hand_side': left_hand_side,
                    'symbol': symbol,
                    'right_hand_side': right_hand_side,
                }
            )

            # Check whether we need to stop the execution.
            if action is not None:
                break

            # Do the transition.
            state, symbol, direction = self.transitions.get(
                (state, symbol),
                (self.reject_state, symbol, 'R'),  # All other transitions are to the reject state.
            )

            if direction == 'R':
                left_hand_side.insert(0, symbol)

                try:
                    symbol = right_hand_side.pop(0)
                except IndexError:
                    # Pretend that we always have a blank symbol on the right.
                    symbol = self.blank_symbol

            elif left_hand_side:
                # Move to the left only if there is a symbold to move.
                right_hand_side.insert(0, symbol)
                symbol = left_hand_side.pop(0)

            else:
                assert direction in 'LR', 'L (left) and R (right) are the only correct directions to move.'
                logging.warning('An attempt to move left from the leftmost cell! The machine stays put.')

    def accepts(self, input_, step_limit=100):
        action = list(islice(self.run(input_), step_limit))[-1][0]

        if action is not None:
            return action == 'Accept'
        else:
            logging.warn(
                'The step limit of %s steps  is reached!',
                step_limit,
            )

    def rejects(self, input_, **kwargs):
        accepts = self.accepts(input_, **kwargs)

        if accepts is not None:
            return not accepts

    def debug(self, input_, step_limit=100, colored=False):
        for action, configuration in islice(self.run(input_), step_limit):
            print(
                '{state:<30} {left}{b}{symbol}{f}{right}'.format(
                    left=''.join(reversed(configuration['left_hand_side'])),
                    right=''.join(configuration['right_hand_side']),
                    b='\x1b[47;1m' if colored else '[',
                    f='\x1b[0m' if colored else ']',
                    **configuration
                )
            )
