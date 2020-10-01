import math
import os
import subprocess
from collections import namedtuple
from copy import copy
import copy
import json

EPSILON = ''


def word_sum(a, b):
    if a == EPSILON:
        return '(1 + {})'.format(b)
    if b == EPSILON:
        return '({} + 1)'.format(a)
    return '({} + {})'.format(a, b)


def word_conj(a, b, symbol):
    if not a:
        return '{}'.format(b)
    if not b:
        return '{}'.format(a)
    return '({}{}{})'.format(a, symbol, b)


def sub_set(set_):
    from itertools import combinations
    answer = set()
    for i in range(len(set_) + 1):
        answer.update({frozenset(j) for j in combinations(set_, i)})

    return answer


def new_word(forbidden):
    i = 0
    word = 's0'
    while word in forbidden:
        i += 1
        word = "s{}".format(i)

    return word


def new_words(num, forbidden):
    counter = 0
    i = 0
    word = 's0'
    answer = []
    while counter < num:
        if word not in forbidden:
            answer.append(copy.copy(word))
            counter += 1
        i += 1
        word = "s{}".format(i)

    return answer


def other_edges(edges):
    new_edges = dict()
    for complex_edges in edges:
        for letter, vertexes in edges[complex_edges].items():
            for node in vertexes:
                pair_ = copy.deepcopy((complex_edges, node))
                if pair_ in new_edges:
                    new_edges[pair_].add(letter)
                else:
                    new_edges.update({pair_: {letter}})
    return new_edges


def add_edge(edges, from_, letter, to_):
    if from_ in edges:
        if letter in edges[from_]:
            edges[from_][letter].update(to_)
        else:
            edges[from_].update({letter: to_})
    else:
        edges.update({from_: {letter: to_}})


class StateMachine(object):
    def __init__(self, nodes: set, edges: map, start: str, final: set, alphabet: set):
        """Constructor"""
        self.nodes = nodes
        self.edges = edges
        self.start = start
        self.final = final
        self.alphabet = alphabet

        self.prepared_files = []

    def _get_edge(self, from_, letter):
        if from_ in self.edges:
            return self.edges[from_][letter]
        else:
            return set()

    def _add_edge(self, from_, letter, to_):
        add_edge(self.edges, from_, letter, to_)

    def _clean_node(self):
        visited = {node_: False for node_ in self.nodes}
        visited[self.start] = True

        new_nodes = {self.start}
        new_edges = dict()
        new_final = set()

        queue = [self.start]
        if self.start in self.final:
            new_final.add(self.start)

        while queue:
            current = queue.pop(0)

            if current in self.edges:
                for letter, vertexes in self.edges[current].items():
                    for node in vertexes:
                        if node in self.final:
                            new_final.add(node)
                        new_nodes.add(node)
                        if not visited[node]:
                            queue.append(node)
                            visited[node] = True
                        add_edge(new_edges, current, letter, {node})

        self.nodes = new_nodes
        self.edges = new_edges
        self.final = new_final

    def __str__(self):
        text = ''
        text += 'nodes:\n'

        for node in self.nodes:
            text += "{}{}\n".format('  ', node)

            if node in self.edges:
                for (letter, vertex_edges) in self.edges[node].items():
                    for edge in vertex_edges:
                        text += "{}{}{}{}\n".format('    ', edge, ' ', letter)

        text += "start: {}\n".format(self.start)
        text += "final: {}\n".format(self.final)

        return text

    def _remove_node(self, removing_node):
        word = ''

        if removing_node in self.edges:
            for letter, nodes in self.edges[removing_node].items():
                if removing_node in nodes:
                    word = letter
                    break

        for node, edge in self.edges.items():
            for letter, node_sets in copy.copy(edge).items():
                if removing_node in node_sets and removing_node in self.edges:
                    for to_letter, to_edges in copy.copy(self.edges[removing_node]).items():
                        if to_edges == removing_node:
                            continue
                        for to_edge in to_edges:
                            self._add_throw_edge(node, letter, removing_node, word, to_edge, to_letter)

        for node, edge in self.edges.items():
            for letter, node_sets in edge.items():
                if removing_node in node_sets:
                    self._erase_edge(node, letter, {removing_node})

        if removing_node in self.edges:
            del self.edges[removing_node]

        self.nodes.remove(removing_node)

    def _make_dump(self):
        return copy.deepcopy({'nodes': self.nodes,
                              'edges': self.edges,
                              'start': self.start,
                              'final': self.final,
                              'alphabet': self.alphabet})

    def _erase_edge(self, from_, letter, to_):
        self.edges[from_][letter] = self.edges[from_][letter] - to_
        if self.edges[from_][letter] == {}:
            del self.edges[from_][letter]

    def _make_tex_node(self, node, num):
        tex_text = '\\node[state'
        if node == self.start:
            tex_text += ', initial'
        if node in self.final:
            tex_text += ', accepting'
        tex_text += ']({})'.format(node)
        angel = 2 * math.pi * num / len(self.nodes)
        tex_text += 'at({}, {})'.format(-math.cos(angel) * 5,
                                        -math.sin(angel) * 5)
        tex_text += '{' + '{}'.format(node) + '};\n'

        return tex_text

    def _clear_edges(self):
        for node, edges in copy.deepcopy(self.edges).items():
            for letter, set_ in copy.copy(edges).items():
                if not set_:
                    del self.edges[node][letter]
            if not edges:
                del self.edges[node]

    @staticmethod
    def _find_direction(i, n):
        print("<", i, " ", n, ">")
        if i == 0:
            return 'right'
        if i < n / 4:
            return 'left'
        if i < n / 2:
            return 'below'
        if i < 3 * n / 4:
            return 'right'
        return 'above'

    def _make_tex_edge(self, letter, num, index, from_, to_):
        if from_ != to_:
            tex_text = '    edge [bend left = {' + '{}'.format(10 + 15 * index) + '}]'
            tex_text += 'node {' + '${}$'.format(letter if letter != '' else '\\varepsilon') + \
                        '}' + '({})'.format(to_)
            tex_text += '\n'

            return tex_text
        else:
            tex_text = '    edge [loop {}]'.format(self._find_direction(num, len(self.nodes)))
            tex_text += 'node {' + '$' + ('\;' * 8) * index + '{}$'.format(
                letter if letter != '' else '\\varepsilon') + '}' + '({})'.format(
                to_)
            tex_text += '\n'

            return tex_text

    def _add_throw_edge(self, from_, from_letter, mid, mid_letter, to_, to_letter):
        if mid_letter:
            word = '({}({})^*{})'.format(from_letter, mid_letter, to_letter)
        else:
            word = word_conj(from_letter, to_letter, '')  # '({}{})'.format(from_letter, to_letter)
        self._add_edge(from_, word, {to_})

        for letter, edge in copy.copy(self.edges[from_]).items():
            if letter != word and to_ in edge:
                mix_word = word_sum(word, letter)
                self._erase_edge(from_, word, {to_})
                self._erase_edge(from_, letter, {to_})

                self._add_edge(from_, mix_word, {to_})

    def make_tex(self, filename):
        subprocess.run('if ! [ -d out ]; then mkdir ./out; fi', shell=True, check=True)

        self.prepared_files.append(filename)
        tex_text = ''
        with open('tex/start', 'r') as begin_file:
            tex_text += begin_file.read() + '\n'

        sort_nodes = list(copy.deepcopy(self.nodes))
        sort_nodes.sort()

        nodes_num = dict()

        for num, node in enumerate(sort_nodes):
            nodes_num.update({node: num})
            tex_text += self._make_tex_node(node, num)

        tex_text += '\n\\path\n'

        new_E = other_edges(self.edges)

        for (from_, to_), letters in new_E.items():
            tex_text += '({})'.format(from_) + '\n'
            for index, letter in enumerate(letters):
                tex_text += self._make_tex_edge(letter, nodes_num[from_], index, from_, to_)

        tex_text += ';\n'

        with open('tex/end', 'r') as end_file:
            tex_text += end_file.read()

        with open('out/{}.tex'.format(filename), 'w') as out_file:
            out_file.write(tex_text)

    def upload_machine(self, filename):
        with open(filename, 'r') as read_file:
            data = json.load(read_file)

        self.nodes = set(data['nodes'])
        self.start = data['start']
        self.final = set(data['final'])
        self.alphabet = set(data['alphabet'])

        for complex_edge in data['edges']:
            self._add_edge(complex_edge[0], complex_edge[1], set(complex_edge[2]))

        print(self.nodes)
        print(self.start)
        print(self.final)
        print(self.edges)

    def prepare_files(self):
        for file in self.prepared_files:
            subprocess.run('pdflatex  -output-directory=out -jobname={} out/{}.tex'.format(file, file), shell=True, check=True)

        for file in self.prepared_files:
            subprocess.run('rm out/{}.log'.format(file), shell=True, check=True)
            subprocess.run('rm out/{}.aux'.format(file), shell=True, check=True)
            # subprocess.run('rm out/{}.tex'.format(file))

        for file in self.prepared_files:
            subprocess.run('open out/{}.pdf'.format(file), shell=True, check=True)

    def remove_epsilon(self):
        new_edges = []

        for node in self.nodes:
            visited = {node_: False for node_ in self.nodes}

            queue = [node]

            while queue:
                current = queue.pop(0)

                if current in self.final:
                    self.final.add(node)

                if current in self.edges:
                    if current != node:
                        for (letter, edge) in self.edges[current].items():
                            if letter != EPSILON:
                                new_edges.append((node, (letter, copy.deepcopy(edge))))

                    if EPSILON in self.edges[current]:
                        for new_node in self.edges[current][EPSILON]:
                            if not visited[new_node]:
                                queue.append(new_node)
                                visited[new_node] = True

        for (out, (letter, to)) in new_edges:
            self._add_edge(out, letter, to)

        for all_edges in self.edges.values():
            all_edges.pop(EPSILON, None)

        if EPSILON in self.alphabet:
            self.alphabet.remove(EPSILON)

    def make_unique_path(self):
        diction = {frozenset({self.start}): '0'}
        new_nodes = {'0'}
        new_edges = dict()
        new_start = '0'
        new_final = set()

        queue = [frozenset({self.start})]
        if self.start in self.final:
            new_final.add(diction[frozenset({self.start})])

        while queue:
            current = queue.pop(0)
            alphabet = set()

            for node in current:
                if node in self.edges:
                    alphabet.update(self.edges[node])
            for letter in alphabet:
                new_set = set()
                is_final = False
                for node in current:
                    if node in self.edges and letter in self.edges[node]:
                        new_set.update(self.edges[node][letter])
                        for vertex in self.edges[node][letter]:
                            if vertex in self.final:
                                is_final = True
                new_set = frozenset(new_set)
                if new_set not in diction or diction[new_set] not in new_nodes:
                    diction.update({new_set: str(len(new_nodes))})
                    new_nodes.add(str(len(new_nodes)))
                    if is_final:
                        new_final.add(diction[new_set])
                    queue.append(new_set)
                if diction[current] in new_edges:
                    if letter in new_edges[diction[current]]:
                        new_edges[diction[current]][letter].add(diction[new_set])
                    else:
                        new_edges[diction[current]].update({letter: {diction[new_set]}})
                else:
                    new_edges.update({diction[current]: {letter: {diction[new_set]}}})

        self.nodes = new_nodes
        self.edges = new_edges
        self.start = new_start
        self.final = new_final

    def make_one_final(self):
        if len(self.final) <= 1:
            return

        new_node = new_word(self.nodes)
        self.nodes.add(new_node)

        for node in self.final:
            self._add_edge(node, EPSILON, {new_node})

        self.final = {new_node}

    def invert_finite(self):
        self.final = self.nodes - self.final

    def make_final(self):
        new_node = new_word(self.nodes)
        self.nodes.add(new_node)

        for node in self.nodes:
            if node in self.edges:
                new_letters = self.alphabet - self.edges[node].keys()
                for letter in new_letters:
                    self._add_edge(node, letter, {new_node})
            else:
                for letter in self.alphabet:
                    self._add_edge(node, letter, {new_node})

    def make_single_edges(self):
        new_edges = dict()
        new_letter = dict()
        for node, edge in self.edges.items():
            for letter, node_sets in copy.copy(edge).items():
                for node_to in node_sets:
                    if (node, node_to) in new_edges:
                        new_edges[(node, node_to)] = word_sum(new_edges[(node, node_to)], letter)
                        self._erase_edge(node, letter, {node_to})
                    else:
                        new_edges.update({(node, node_to): letter})
                        new_letter.update({(node, node_to): letter})
                        self._erase_edge(node, letter, {node_to})
        for (from_, to_), letter in new_letter.items():
            self._add_edge(from_, new_edges[(from_, to_)], {to_})
        self._clear_edges()

    def remove_all(self):
        self.make_single_edges()
        self.make_one_final()
        for num, node in enumerate(copy.copy(self.nodes)):
            if node not in self.final and node != self.start:
                self._remove_node(node)
                self.make_tex(num)

    def get_invert_language(self, file_name):
        self.remove_epsilon()
        self.make_unique_path()
        self.make_final()
        self.invert_finite()
        self.remove_all()
        self.get_regular(file_name)

    def make_0_1_edges(self):
        for node, edge in copy.deepcopy(self.edges).items():
            for letter, node_sets in copy.copy(edge).items():
                if len(letter) > 1:
                    new_nodes = new_words(len(letter) - 1, self.nodes)
                    self._erase_edge(node, letter, node_sets)

                    self._add_edge(node, letter[0], {new_nodes[0]})
                    self._add_edge(new_nodes[-1], letter[-1], node_sets)

                    if len(letter) > 2:
                        for i in range(len(new_nodes) - 1):
                            self._add_edge(new_nodes[i], letter[i + 1], {new_nodes[i + 1]})

                    self.nodes.update(new_nodes)
        self._clear_edges()

    def make_regular_tex(self, filename, text):
        subprocess.run("if ! [ -f ./out ]; then\nmkdir ./out\nfi\n")

        self.prepared_files.append(filename)
        tex_text = ''
        with open('tex/start', 'r') as begin_file:
            tex_text += begin_file.read() + '\n'

        tex_text += '${}$'.format(text)

        with open('tex/end', 'r') as end_file:
            tex_text += end_file.read()

        with open('out/{}.tex'.format(filename), 'w') as out_file:
            out_file.write(tex_text)

    def get_regular(self, file_name):
        if len(self.nodes) == 1:
            for node, edge in self.edges.items():
                for word, _ in edge:
                    return word
            return None

        if len(self.nodes) == 2:
            a = self.start
            b = ''

            for node in self.nodes:
                if node != a:
                    b = node

            loop_a = ''
            loop_b = ''

            a_b_edge = ''
            b_a_edge = ''

            if a in self.edges:
                for letter, to_ in self.edges[a].items():
                    if a in to_:
                        loop_a = letter
                    if b in to_:
                        a_b_edge = letter

            if b in self.edges:
                for letter, to_ in self.edges[b].items():
                    if b in to_:
                        loop_b = letter
                    if a in to_:
                        b_a_edge = letter

            text = ''

            if b_a_edge:
                text += '{}^*'.format(loop_a)
                text += '{}^*'.format(a_b_edge)
                text += '('
                text += '{}^*+'.format(loop_b)
                if loop_a:
                    text += '{} {}^*{}'.format(b_a_edge, loop_a, a_b_edge)
                else:
                    text += '{} {}'.format(b_a_edge, a_b_edge)
                text += ')^*'
            else:
                text += '{}^*'.format(loop_a) if loop_a else ''
                text += '{}'.format(a_b_edge) if a_b_edge else ''
                text += '{}^*'.format(loop_b) if loop_b else ''

            self.make_regular_tex(file_name, text)

    def _improve_states_enumeration(self, last_dict):
        sets = dict()
        enumeration = dict()
        for node in self.nodes:
            enumeration.update({node: dict()})
            current_dict = dict()
            Complex_edge = namedtuple("Complex_edge", "letter nodes_set")
            current_dict_hashable = set()
            for letter, edge in self.edges[node].items():
                current_dict.update({letter: {last_dict[node_] for node_ in edge}})
                current_dict_hashable.add(Complex_edge(letter, frozenset({last_dict[node_] for node_ in edge})))
            current_dict_hashable = frozenset(current_dict_hashable)
            if current_dict_hashable in sets:
                enumeration.update({node: sets[current_dict_hashable]})
            else:
                enumeration.update({node: len(sets)})
                sets.update({current_dict_hashable: len(sets)})
        return enumeration, len(sets)

    def _make_state_enumeration(self):
        enumeration = {node: 1 if node in self.final else 0 for node in self.nodes}
        num_sz = 2
        last = 0
        while last != num_sz:
            last = num_sz
            enumeration, num_sz = self._improve_states_enumeration(enumeration)

        return enumeration, num_sz

    def simplify(self):
        enumeration, sz = self._make_state_enumeration()
        for a in enumeration:
            enumeration[a] = str(enumeration[a])
        new_edges = dict()

        for node, edges in self.edges.items():
            for letter, set_edges in edges.items():
                add_edge(new_edges, enumeration[node], letter, {enumeration[x] for x in set_edges})
        self.nodes = {str(i) for i in range(sz)}
        self.edges = new_edges
        self.start = enumeration[self.start]
        self.final = {enumeration[x] for x in self.final}


def are_homomorphic(machine_a, machine_b):
    isomorphism = {machine_a.start: machine_b.start}

    def update_isomorphism(isomorphism_, a, b):
        if a not in isomorphism_:
            isomorphism_.update({a: b})
            return True
        else:
            if isomorphism_[a] == b:
                return True
            else:
                return False

    queue = [machine_a.start]
    used = set(machine_a.start)

    while queue:
        current = queue.pop(0)
        if current in machine_a.edges:
            for letter, a_edges in machine_a.edges[current].items():
                if len(a_edges) > 1:
                    raise ValueError("ambiguous edge")

                b_edges = machine_b._get_edge(isomorphism[current], letter)
                if len(b_edges) > 1:
                    raise ValueError("ambiguous edge")

                if len(a_edges) != len(b_edges):
                    return False

                for node_b in b_edges:
                    for node_a in a_edges:
                        if not update_isomorphism(isomorphism, node_a, node_b):
                            return False
                        else:
                            if node_a not in used:
                                used.add(node_a)
                                queue.append(node_a)

    for node_a in machine_a.final:
        if isomorphism[node_a] not in machine_b.final:
            return False

    return True


def are_equal(machine_a: StateMachine, machine_b: StateMachine):
    if machine_a.alphabet != machine_b.alphabet:
        return False

    x = are_homomorphic(machine_a, machine_b)
    y = are_homomorphic(machine_b, machine_a)
    return x and y
