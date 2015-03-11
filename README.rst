====================================
Turing Machine as a Python Generator
====================================

.. image:: https://travis-ci.org/dimazest/turing_machine.svg?branch=master
    :target: https://travis-ci.org/dimazest/turing_machine

This is a simulator of a Turing machine with a singly-infinite tape. The
simulator allows one to execute a machine step-by step, check whether a machine
accepts or rejects a particular input and see it's execution.

.. contents::

Installation
============

There are several ways of getting the simulator.

* **PyPi**: great if you want to use the package as part of your
  application::

      pip install turing_machine

* **git**: if you want to get all the files, most importantly `the notebook`_::

      git clone https://github.com/dimazest/turing_machine.git

* **github**: if you don't bother using git::

      wget https://github.com/dimazest/turing_machine/archive/master.zip

Using the simulator in the IPython notebook
===========================================

`The notebook`_ (``Turing machine.ipynb``) is a great way to run the machine
interactively. You need to have a fresh version of IPython installed (>=3.0).
Check out `these IPython installation instructions using miniconda`__ if you
don't have it installed yet.

__ http://eecs.io/python-environment-for-scientific-computing.html

.. _`the notebook`: http://nbviewer.ipython.org/github/dimazest/turing_machine/blob/master/Turing%20machine.ipynb

Using the simulator inside of a Python script
=============================================

If you dont want to be bother with IPython, you can use the simulator inside of
your own script, see ``w_hash_w.py``, for example::

    python w_hash_w.py
    q0                             [1]0#10
    FindDelimiter1                 X[0]#10
    FindDelimiter1                 X0[#]10

    ...    MANY OTHER CONFIGURATIONS   ...

    qa                             XX#XX[]

The API
=======

The package provides the ```TuringMachine`` class which is instantiated with
particular transitions. Once a Turing Machine is instantiated it can be
executed. Here is an example of a machine that accepts language `w#w` (two
identical words separated by ``#``).

>>> from turing_machine import TuringMachine


>>> w_hash_w = TuringMachine(
...     {
...         ('q0', '#'): ('End', '#', 'R'),
...         ('End', ''): ('qa', '', 'R'),
...
...         ('q0', '0'): ('FindDelimiter0', 'X', 'R'),
...         ('FindDelimiter0', '#'): ('Check0', '#', 'R'),
...         ('Check0', '0'): ('FindLeftmost', 'X', 'L'),
...
...         ('q0', '1'): ('FindDelimiter1', 'X', 'R'),
...         ('FindDelimiter1', '#'): ('Check1', '#', 'R'),
...         ('Check1', '1'): ('FindLeftmost', 'X', 'L'),
...
...         ('FindLeftmost', '0'): ('FindLeftmost', '0', 'L'),
...         ('FindLeftmost', '1'): ('FindLeftmost', '1', 'L'),
...         ('FindLeftmost', 'X'): ('FindLeftmost', 'X', 'L'),
...         ('FindLeftmost', '#'): ('FindLeftmost', '#', 'L'),
...         ('FindLeftmost', ''): ('FindNext', '', 'R'),
...
...         ('FindNext', 'X'): ('FindNext', 'X', 'R'),
...         ('FindNext', '0'): ('FindDelimiter0', 'X', 'R'),
...         ('FindNext', '1'): ('FindDelimiter1', 'X', 'R'),
...         ('FindNext', '#'): ('End', '#', 'R'),
...
...         ('FindDelimiter0', '0'): ('FindDelimiter0', '0', 'R'),
...         ('FindDelimiter0', '1'): ('FindDelimiter0', '1', 'R'),
...         ('FindDelimiter1', '0'): ('FindDelimiter1', '0', 'R'),
...         ('FindDelimiter1', '1'): ('FindDelimiter1', '1', 'R'),
...
...         ('Check0', 'X'): ('Check0', 'X', 'R'),
...         ('Check1', 'X'): ('Check1', 'X', 'R'),
...
...         ('End', 'X'): ('End', 'X', 'R'),
...     }
... )

Input acceptance
----------------

Once we got a machine, we can check whether it accepts a particular string:

>>> w_hash_w.accepts('#')
True
>>> w_hash_w.accepts('1#1')
True
>>> w_hash_w.accepts('1#10')
False

or rejects:

>>> w_hash_w.rejects('##')
True
>>> w_hash_w.rejects('#')
False

Step by step execution
----------------------

The ``.run()`` method returns a generator that executes the machine and yields
the configuration together with he acceptance decision:

>>> execution = w_hash_w.run('1#1')
>>> action, context = next(execution)
>>> context['state']
'q0'

Infinite execution
------------------

Because execution is done in a generator, it's possible to have infinite
executions but the acceptance checks are limited by the number of steps they are
allowed to perform.

>>> go_right = TuringMachine(
...     {
...         ('q0', ''): ('q0', '', 'R'),
...     }
... )

If the step limit is reached, ``None`` is returned:

>>> go_right.accepts('') is None
True

Do 2000 steps:

>>> go_right.accepts('', step_limit=2000) is None
True

Debugging
---------

Another nice feature is the ability to debug the machine by observing it's
configuration.


>>> w_hash_w.debug('1#1')
q0                             [1]#1
FindDelimiter1                 X[#]1
Check1                         X#[1]
FindLeftmost                   X[#]X
FindLeftmost                   [X]#X
FindLeftmost                   []X#X
FindNext                       [X]#X
FindNext                       X[#]X
End                            X#[X]
End                            X#X[]
qa                             X#X[]
