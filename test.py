import pytest

from machine import StateMachine
from machine import are_equal


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


def prepare_machine(num_nodes, single_edges, start, finish, alphabet):
    nodes = {'s' + str(i) for i in range(num_nodes)}
    edges = {'s' + str(i): dict() for i in range(num_nodes)}

    for from_, letter, to_ in single_edges:
        edges[from_].update({letter: to_})

    return StateMachine(nodes, edges, start, finish, alphabet)


def parse_machine(machine_info):
    return StateMachine(machine_info['nodes'], machine_info['edges'], machine_info['start'],
                        machine_info['final'], machine_info['alphabet'])


@pytest.mark.parametrize("num_nodes,single_edges,start,finish,alphabet,"
                         "num_nodes2,single_edges2,start2,finish2,alphabet2, expected", [
                             (
                                     3, [
                                         ('s0', '', {'s1'}),
                                         ('s1', 'a', {'s2'})
                                     ], 's0', {'s1'}, {'a', 'b', ''},
                                     3, [
                                         ('s0', '', {'s1'}),
                                         ('s1', 'a', {'s2'})
                                     ], 's0', {'s1'}, {'a', 'b', ''},
                                     True
                             ),
                             (
                                     3, [
                                         ('s1', '', {'s2'}),
                                         ('s2', 'a', {'s0'})
                                     ], 's1', {'s2'}, {'a', 'b', ''},
                                     3, [
                                         ('s0', '', {'s1'}),
                                         ('s1', 'a', {'s2'})
                                     ], 's0', {'s1'}, {'a', 'b', ''},
                                     True
                             ),
                             (
                                     3, [
                                         ('s1', '', {'s2'}),
                                         ('s2', 'a', {'s2'})
                                     ], 's1', {'s2'}, {'a', 'b', ''},
                                     3, [
                                         ('s0', '', {'s1'}),
                                         ('s1', 'a', {'s2'})
                                     ], 's0', {'s1'}, {'a', 'b', ''},
                                     False
                             )
                         ])
def test_make_are_equal(num_nodes, single_edges, start, finish, alphabet,
                        num_nodes2, single_edges2, start2, finish2, alphabet2, expected):
    assert are_equal(prepare_machine(num_nodes, single_edges, start, finish, alphabet),
                     prepare_machine(num_nodes2, single_edges2, start2, finish2, alphabet2)) == expected


@pytest.mark.parametrize("num_nodes,single_edges,start,finish,alphabet,expected", [
    (
            6, [
                ('s0', 'a', {'s1', 's2'}),
                ('s1', 'b', {'s3', 's4'}),
                ('s2', 'b', {'s5', 's6', 's7'})
            ], 's0', {'s1'}, {'a', 'b', ''}, {
                'nodes': {'0', '1', '2'},
                'edges': {'0': {'a': {'1'}}, '1': {'b': {'2'}}},
                'start': '0',
                'final': {'1'},
                'alphabet': {'b', 'a', ''}
            }
    ),
    (
            6, [
                ('s0', 'a', {'s2', 's3'}),
                ('s0', 'b', {'s1'}),
                ('s3', 'a', {'s4', 's5'})
            ], 's0', {'s4'}, {'a', 'b', ''}, {
                'alphabet': {'', 'b', 'a'},
                'edges': {'0': {'a': {'2'}, 'b': {'1'}}, '2': {'a': {'3'}}},
                'final': {'3'},
                'nodes': {'1', '0', '2', '3'},
                'start': '0'
            }
    )
])
def test_make_unique_path(num_nodes, single_edges, start, finish, alphabet, expected):
    machine = prepare_machine(num_nodes, single_edges, start, finish, alphabet)
    machine.make_unique_path()

    assert are_equal(parse_machine(expected), machine)


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
                'alphabet': {'a', 'b'}
            }
    ),
    (
            4, [
                ('s0', '', {'s1', 's2'}),
                ('s1', 'a', {'s3'}),
                ('s2', 'a', {'s3'})
            ], 's0', {'s1'}, {'a', 'b', ''}, {
                'nodes': {'s0', 's2', 's1', 's3'},
                'edges': {
                    's0': {'a': {'s3'}},
                    's1': {'a': {'s3'}},
                    's2': {'a': {'s3'}}, 's3': {}
                },
                'start': 's0',
                'final': {'s0', 's1'},
                'alphabet': {'a', 'b'}
            }
    ),
    (
            6, [
                ('s0', '', {'s1'}),
                ('s1', '', {'s2', 's3'}),
                ('s2', 'a', {'s4'}),
                ('s3', 'a', {'s5'})
            ], 's0', {'s1'}, {'a', 'b', ''}, {
                'alphabet': {'a', 'b'},
                'edges': {'s0': {'a': {'s5', 's4'}},
                          's1': {'a': {'s5', 's4'}},
                          's2': {'a': {'s4'}},
                          's3': {'a': {'s5'}},
                          's4': {},
                          's5': {}},
                'final': {'s1', 's0'},
                'nodes': {'s1', 's2', 's4', 's5', 's3', 's0'},
                'start': 's0'
            }
    )
])
def test_remove_epsilon(num_nodes, single_edges, start, finish, alphabet, expected):
    machine = prepare_machine(num_nodes, single_edges, start, finish, alphabet)
    machine.remove_epsilon()

    assert expected == machine._make_dump()


@pytest.mark.parametrize("num_nodes,single_edges,start,finish,alphabet,expected", [
    (
            3, [
                ('s0', '', {'s1'}),
                ('s1', 'a', {'s2'})
            ], 's0', {'s1'}, {'a', 'b', ''}, {'alphabet': {'', 'b', 'a'},
                                              'edges': {'s0': {'': {'s1'}, 'a': {'s3'}, 'b': {'s3'}},
                                                        's1': {'': {'s3'}, 'a': {'s2'}, 'b': {'s3'}},
                                                        's2': {'': {'s3'}, 'a': {'s3'}, 'b': {'s3'}},
                                                        's3': {'': {'s3'}, 'a': {'s3'}, 'b': {'s3'}}},
                                              'final': {'s1'},
                                              'nodes': {'s0', 's1', 's3', 's2'},
                                              'start': 's0'}
    ), (
            4, [
                ('s0', '', {'s1', 's2'}),
                ('s1', 'a', {'s3'}),
                ('s2', 'a', {'s3'})
            ], 's0', {'s1'}, {'a', 'b', ''}, {'alphabet': {'', 'a', 'b'},
                                              'edges': {'s0': {'': {'s2', 's1'}, 'a': {'s4'}, 'b': {'s4'}},
                                                        's1': {'': {'s4'}, 'a': {'s3'}, 'b': {'s4'}},
                                                        's2': {'': {'s4'}, 'a': {'s3'}, 'b': {'s4'}},
                                                        's3': {'': {'s4'}, 'a': {'s4'}, 'b': {'s4'}},
                                                        's4': {'': {'s4'}, 'a': {'s4'}, 'b': {'s4'}}},
                                              'final': {'s1'},
                                              'nodes': {'s4', 's0', 's2', 's1', 's3'},
                                              'start': 's0'}
    ),
    (
            6, [
                ('s0', '', {'s1'}),
                ('s1', '', {'s2', 's3'}),
                ('s2', 'a', {'s4'}),
                ('s3', 'a', {'s5'})
            ], 's0', {'s1'}, {'a', 'b', ''}, {'alphabet': {'', 'a', 'b'},
                                              'edges': {'s0': {'': {'s1'}, 'a': {'s6'}, 'b': {'s6'}},
                                                        's1': {'': {'s3', 's2'}, 'a': {'s6'}, 'b': {'s6'}},
                                                        's2': {'': {'s6'}, 'a': {'s4'}, 'b': {'s6'}},
                                                        's3': {'': {'s6'}, 'a': {'s5'}, 'b': {'s6'}},
                                                        's4': {'': {'s6'}, 'a': {'s6'}, 'b': {'s6'}},
                                                        's5': {'': {'s6'}, 'a': {'s6'}, 'b': {'s6'}},
                                                        's6': {'': {'s6'}, 'a': {'s6'}, 'b': {'s6'}}},
                                              'final': {'s1'},
                                              'nodes': {'s6', 's1', 's0', 's3', 's2', 's5', 's4'},
                                              'start': 's0'}
    )
])
def test_make_final(num_nodes, single_edges, start, finish, alphabet, expected):
    machine = prepare_machine(num_nodes, single_edges, start, finish, alphabet)
    machine.make_final()

    assert expected == machine._make_dump()


@pytest.mark.parametrize("num_nodes,single_edges,start,finish,alphabet,expected", [
    (
            5, [
                ('s0', '', {'s1', 's4'}),
                ('s1', 'a', {'s2'})
            ], 's0', {'s1', 's2', 's4'}, {'a', 'b', ''}, {
                'alphabet': {'', 'a', 'b'},
                'edges': {'s0': {'': {'s4', 's1'}, 'a': {'s5'}, 'b': {'s5'}},
                          's1': {'': {'s5'}, 'a': {'s2'}, 'b': {'s5'}},
                          's2': {'': {'s5'}, 'a': {'s5'}, 'b': {'s5'}},
                          's3': {'': {'s5'}, 'a': {'s5'}, 'b': {'s5'}},
                          's4': {'': {'s5'}, 'a': {'s5'}, 'b': {'s5'}},
                          's5': {'': {'s5'}, 'a': {'s5'}, 'b': {'s5'}}},
                'final': {'s4', 's2', 's1'},
                'nodes': {'s4', 's2', 's3', 's0', 's5', 's1'},
                'start': 's0'}
    ),
])
def test_make_one_final(num_nodes, single_edges, start, finish, alphabet, expected):
    machine = prepare_machine(num_nodes, single_edges, start, finish, alphabet)
    machine.make_final()

    assert expected == machine._make_dump()


@pytest.mark.parametrize("num_nodes,single_edges,start,finish,alphabet,expected", [
    (
            5, [],
            's0', {'s1', 's2', 's4'}, {'a', 'b', ''}, {
                'alphabet': {'', 'a', 'b'},
                'edges': {'s0': {}, 's1': {}, 's2': {}, 's3': {}, 's4': {}},
                'final': {'s0', 's3'},
                'nodes': {'s4', 's2', 's3', 's0', 's1'},
                'start': 's0'
            }
    ),
])
def test_invert_finite(num_nodes, single_edges, start, finish, alphabet, expected):
    machine = prepare_machine(num_nodes, single_edges, start, finish, alphabet)
    machine.invert_finite()

    assert expected == machine._make_dump()


@pytest.mark.parametrize("num_nodes,single_edges,start,finish,alphabet,expected", [
    (
        3, [
            ('s0', '', {'s1', 's2'}),
            ('s0', 'b', {'s1', 's2'}),
            ('s1', 'a', {'s1', 's0'})
        ], 's0', {'s1'}, {'a', 'b', ''}, {
            'alphabet': {'', 'b', 'a'},
            'edges': {'s0': {'(1 + b)': {'s2', 's1'}},
                      's1': {'a': {'s1', 's0'}}},
            'final': {'s1'},
            'nodes': {'s2', 's1', 's0'},
            'start': 's0'}
    ),
])
def test_make_single_edges(num_nodes, single_edges, start, finish, alphabet, expected):
    machine = prepare_machine(num_nodes, single_edges, start, finish, alphabet)
    machine.make_single_edges()

    assert expected == machine._make_dump()


@pytest.mark.parametrize("num_nodes,single_edges,start,finish,alphabet,expected", [
    (
        3, [
            ('s0', '', {'s1', 's2'}),
            ('s0', 'abc', {'s1', 's2'}),
            ('s1', 'ac', {'s1', 's0'})
        ], 's0', {'s1'}, {'a', 'b', 'c', ''}, {
            'alphabet': {'', 'c', 'b', 'a'},
            'edges': {'s0': {'': {'s1', 's2'}, 'a': {'s3'}},
                      's1': {'a': {'s5'}},
                      's3': {'b': {'s4'}},
                      's4': {'c': {'s1', 's2'}},
                      's5': {'c': {'s0', 's1'}}},
            'final': {'s1'},
            'nodes': {'s4', 's2', 's5', 's0', 's1', 's3'},
            'start': 's0'}
    ),
])
def test_make_0_1_edges(num_nodes, single_edges, start, finish, alphabet, expected):
    machine = prepare_machine(num_nodes, single_edges, start, finish, alphabet)
    machine.make_0_1_edges()

    assert expected == machine._make_dump()
