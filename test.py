import pytest
from main import StateMachine


def setup():
    print("basic setup into module")


def teardown():
    print("basic teardown into module")


def setup_module(module):
    print("module setup")


def teardown_module(module):
    print("module teardown")


def setup_function(function):
    print("function setup")


def teardown_function(function):
    print("function teardown")


@pytest.mark.parametrize("num_nodes,single_edges,start,finish,alphabet,expected", [
    (
        6, [
            ('s0', 'a', {'s1', 's2'}),
            ('s1', 'b', {'s3', 's4'}),
            ('s2', 'b', {'s5', 's6', 's7'})
        ], 's0', {'s1'}, {'a', 'b', ''}, {'nodes': {'0'}, 'edges': {}, 'start': '0', 'final': set(), 'alphabet': {'b', 'a'}}
    ), (
        6, [
            ('s0', 'a', {'s2', 's3'}),
            ('s0', 'b', {'s1'}),
            ('s3', 'a', {'s4', 's5'})
        ], 's0', {'s4'}, {'a', 'b', ''}, {}
    ), (
        2, [], 's0', {'s1'}, {'a', 'b'}, {}
    ), (
        2, [], 's0', {'s0'}, {'a', 'b'}, {}
    )
])
def test_make_unique_path(num_nodes, single_edges, start, finish, alphabet, expected):
    nodes = {'s' + str(i) for i in range(num_nodes)}
    edges = {'s' + str(i): dict() for i in range(num_nodes)}

    for from_, letter, to_ in single_edges:
        edges[from_].update({letter: to_})

    automata = StateMachine(nodes, edges, start, finish, alphabet)
    automata.make_unique_path()

    print(automata.make_dump())

    assert expected == automata.make_dump()


@pytest.mark.parametrize("num_nodes,single_edges,start,finish,alphabet,expected", [
    (
        3, [
            ('s0', '', {'s1'}),
            ('s1', 'a', {'s2'})
        ], 's0', {'s1'}, {'a', 'b', ''}, {
            'nodes': {'s0', 's2', 's1'},
            'edges': {'s0': {'a': {'s2'}}, 's1': {'a': {'s2'}}, 's2': {}},
            'start': 's0',
            'final': {'s0', 's1'},
            'alphabet': {'', 'a', 'b'}}
    ), (
        4, [
            ('s0', '', {'s1', 's2'}),
            ('s1', 'a', {'s3'}),
            ('s2', 'a', {'s3'})
        ], 's0', {'s1'}, {'a', 'b', ''}, {
            'nodes': {'s0', 's2', 's1', 's3'},
            'edges': {'s0': {'a': {'s3'}}, 's1': {'a': {'s3'}}, 's2': {'a': {'s3'}}, 's3': {}},
            'start': 's0',
            'final': {'s0', 's1'},
            'alphabet': {'', 'a', 'b'}}
    ),
    (
        6, [
            ('s0', '', {'s1'}),
            ('s1', '', {'s2', 's3'}),
            ('s2', 'a', {'s4'}),
            ('s3', 'a', {'s5'})
        ], 's0', {'s1'}, {'a', 'b', ''}, {
            'alphabet': {'', 'a', 'b'},
             'edges': {'s0': {'a': {'s5', 's4'}},
                       's1': {'a': {'s5', 's4'}},
                       's2': {'a': {'s4'}},
                       's3': {'a': {'s5'}},
                       's4': {},
                       's5': {}},
             'final': {'s1', 's0'},
             'nodes': {'s1', 's2', 's4', 's5', 's3', 's0'},
             'start': 's0'}
    )
])
def test_remove_epsilon(num_nodes, single_edges, start, finish, alphabet, expected):
    nodes = {'s' + str(i) for i in range(num_nodes)}
    edges = {'s' + str(i): dict() for i in range(num_nodes)}

    for from_, letter, to_ in single_edges:
        edges[from_].update({letter: to_})

    automata = StateMachine(nodes, edges, start, finish, alphabet)
    automata.remove_epsilon()

    print(automata.make_dump())

    assert expected == automata.make_dump()
