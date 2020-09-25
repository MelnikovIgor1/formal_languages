import math
import os
from copy import copy
import copy
import json


Epsilon = ''



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
            answer.append(copy(word))
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
    def __init__(self, nodes, edges, start, final, alphabet):
        """Constructor"""
        self.nodes = nodes  # set
        self.edges = edges  # map(str, map(str, set))
        self.start = start  # str
        self.final = final  # set
        self.Alphabet = alphabet  # set

        self.prepared_files = []

    def add_edge(self, from_, letter, to_):
        add_edge(self.edges, from_, letter, to_)

    def clean_node(self):
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
                            if letter != Epsilon:
                                new_edges.append((node, (letter, copy.deepcopy(edge))))

                    if Epsilon in self.edges[current]:
                        for new_node in self.edges[current][Epsilon]:
                            if not visited[new_node]:
                                queue.append(new_node)
                                visited[new_node] = True

        for (out, (letter, to)) in new_edges:
            self.add_edge(out, letter, to)

        for all_edges in self.edges.values():
            all_edges.pop(Epsilon, None)

    @staticmethod
    def make_node_list(nodes):
        node_copy = []  # list(self.nodes)
        for node in nodes:
            if type(node) == frozenset:
                node_copy.append(jsonpickle.encode(node))
            else:
                node_copy.append(node)

        return node_copy

    def make_unique_path(self):
        diction = {frozenset({self.start}): '0'}
        new_nodes = {'0'}
        new_edges = dict()
        new_start = '0'  # frozenset({self.start})
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

    def make_dump(self):
        return copy.deepcopy({'nodes': self.nodes,
                              'edges': self.edges,
                              'start': self.start,
                              'final': self.final,
                              'alphabet': self.Alphabet})

    def make_one_final(self):
        if len(self.final) <= 1:
            return

        new_node = new_word(self.nodes)
        self.nodes.add(new_node)

        for node in self.final:
            self.add_edge(node, Epsilon, {new_node})

        self.final = {new_node}

    def invert_finite(self):
        self.final = self.nodes - self.final

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

    @staticmethod
    def find_direction(i, n):
        print("<", i, " ", n, ">")
        if i == 0:
            return 'right'
        if i < n/4:
            return 'left'
        if i < n/2:
            return 'below'
        if i < 3*n/4:
            return 'right'
        return 'above'

    def _make_tex_edge(self, letter, num, from_, to_):
        if from_ != to_:
            tex_text = '    edge [bend left = {' + '{}'.format(10 + 15 * num) + '}]'
            tex_text += 'node {' + '${}$'.format(letter if letter != '' else '\\varepsilon') + '}' + '({})'.format(
                to_)
            tex_text += '\n'

            return tex_text
        else:
            tex_text = '    edge [loop {}]'.format(self.find_direction(num, len(self.nodes)))
            tex_text += 'node {' + '${}$'.format(letter if letter != '' else '\\varepsilon') + '}' + '({})'.format(
                to_)
            tex_text += '\n'

            return tex_text

    def make_tex(self, filename):
        os.system("if ! [ -f ./out ]; then\nmkdir ./out\nfi\n")
        
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
            for num, letter in enumerate(letters):
                tex_text += self._make_tex_edge(letter, nodes_num[from_], from_, to_)

        tex_text += ';\n'

        with open('tex/end', 'r') as end_file:
            tex_text += end_file.read()

        with open('out/{}.tex'.format(filename), 'w') as out_file:
            out_file.write(tex_text)

    def upload_automata(self, filename):
        with open(filename, 'r') as read_file:
            data = json.load(read_file)

        self.nodes = set(data['nodes'])
        self.start = data['start']
        self.final = set(data['final'])
        self.Alphabet = set(data['alphabet'])

        for complex_edge in data['edges']:
            self.add_edge(complex_edge[0], complex_edge[1], set(complex_edge[2]))

        print(self.nodes)
        print(self.start)
        print(self.final)
        print(self.edges)

    def prepare_files(self):
        for file in self.prepared_files:
            os.system('pdflatex  -output-directory=out -jobname={} out/{}.tex'.format(file, file))

        for file in self.prepared_files:
            os.system('rm out/{}.log'.format(file))
            os.system('rm out/{}.aux'.format(file))
            # os.system('rm out/{}.tex'.format(file))

        for file in self.prepared_files:
            os.system('open out/{}.pdf'.format(file))

