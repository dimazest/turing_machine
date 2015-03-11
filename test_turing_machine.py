# -*- coding: utf-8 -*-
import sys

import pytest

from turing_machine import TuringMachine


@pytest.fixture
def transitions():
    return {
        ('q0', '#'): ('End', '#', 'R'),
        ('End', ''): ('qa', '', 'R'),

        ('q0', '0'): ('FindDelimiter0', 'X', 'R'),
        ('FindDelimiter0', '#'): ('Check0', '#', 'R'),
        ('Check0', '0'): ('FindLeftmost', 'X', 'L'),

        ('q0', '1'): ('FindDelimiter1', 'X', 'R'),
        ('FindDelimiter1', '#'): ('Check1', '#', 'R'),
        ('Check1', '1'): ('FindLeftmost', 'X', 'L'),

        ('FindLeftmost', '0'): ('FindLeftmost', '0', 'L'),
        ('FindLeftmost', '1'): ('FindLeftmost', '1', 'L'),
        ('FindLeftmost', 'X'): ('FindLeftmost', 'X', 'L'),
        ('FindLeftmost', '#'): ('FindLeftmost', '#', 'L'),
        ('FindLeftmost', ''): ('FindNext', '', 'R'),

        ('FindNext', 'X'): ('FindNext', 'X', 'R'),
        ('FindNext', '0'): ('FindDelimiter0', 'X', 'R'),
        ('FindNext', '1'): ('FindDelimiter1', 'X', 'R'),
        ('FindNext', '#'): ('End', '#', 'R'),

        ('FindDelimiter0', '0'): ('FindDelimiter0', '0', 'R'),
        ('FindDelimiter0', '1'): ('FindDelimiter0', '1', 'R'),
        ('FindDelimiter1', '0'): ('FindDelimiter1', '0', 'R'),
        ('FindDelimiter1', '1'): ('FindDelimiter1', '1', 'R'),

        ('Check0', 'X'): ('Check0', 'X', 'R'),
        ('Check1', 'X'): ('Check1', 'X', 'R'),

        ('End', 'X'): ('End', 'X', 'R')
    }


@pytest.fixture
def machine(transitions):
    return TuringMachine(transitions)


def test_accepts(machine):
    assert machine.accepts('11110011001010#11110011001010', step_limit=1000)
    assert machine.accepts('11110011001010#11110011001010', step_limit=2) is None


def test_rejects(machine):
    assert machine.rejects('1000#10001')


@pytest.mark.parametrize(
    'input_',
    (
        '',
        [],
        [''],
    )

)
def test_empy_input(machine, input_):
    assert machine.rejects(input_)


@pytest.mark.parametrize(
    'transitions',
    (
        {('q0', ''): ('q0', '', 'L')},
    )
)
def test_go_left(machine):
    execution = machine.run('')

    assert next(execution) == (
        None,
        {
            'left_hand_side': [''],
            'right_hand_side': [],
            'state': 'q0',
            'symbol': '',
        },
    )

    for _ in range(3):
        assert next(execution) == (
            None,
            {
                'left_hand_side': [],
                'right_hand_side': [''],
                'state': 'q0',
                'symbol': '',
            },
        )


@pytest.mark.parametrize(
    ('colored', 'begin_marker', 'end_marker'),
    (
        (False, '[', ']'),
        (True, '\x1b[47;1m', '\x1b[0m'),
    ),
)
def test_debug(machine, capsys, begin_marker, end_marker, colored):
    machine.debug('101X101', colored=colored)
    out, err = capsys.readouterr()

    assert not err

    assert out == (
        'q0                             {b}1{e}01X101\n'
        'FindDelimiter1                 X{b}0{e}1X101\n'
        'FindDelimiter1                 X0{b}1{e}X101\n'
        'FindDelimiter1                 X01{b}X{e}101\n'
        'qr                             X01X{b}1{e}01\n'
        ''.format(b=begin_marker, e=end_marker)
    )


def test_scrip_w_hash_w(capsys):
    if 'w_hash_w' in sys.modules:
        del sys.modules['w_hash_w']
    import w_hash_w

    out, err = capsys.readouterr()

    assert not err

    assert out == (
        'q0                             [1]0#10\n'
        'FindDelimiter1                 X[0]#10\n'
        'FindDelimiter1                 X0[#]10\n'
        'Check1                         X0#[1]0\n'
        'FindLeftmost                   X0[#]X0\n'
        'FindLeftmost                   X[0]#X0\n'
        'FindLeftmost                   [X]0#X0\n'
        'FindLeftmost                   []X0#X0\n'
        'FindNext                       [X]0#X0\n'
        'FindNext                       X[0]#X0\n'
        'FindDelimiter0                 XX[#]X0\n'
        'Check0                         XX#[X]0\n'
        'Check0                         XX#X[0]\n'
        'FindLeftmost                   XX#[X]X\n'
        'FindLeftmost                   XX[#]XX\n'
        'FindLeftmost                   X[X]#XX\n'
        'FindLeftmost                   [X]X#XX\n'
        'FindLeftmost                   []XX#XX\n'
        'FindNext                       [X]X#XX\n'
        'FindNext                       X[X]#XX\n'
        'FindNext                       XX[#]XX\n'
        'End                            XX#[X]X\n'
        'End                            XX#X[X]\n'
        'End                            XX#XX[]\n'
        'qa                             XX#XX[]\n'
    )
