import sys


class Root(object):
    def __init__(self):
        self.nodes = []

    def out(self):
        for node in self.nodes:
            node.out()


class Node(object):
    def __init__(self, name, indent, parent):
        self.name = name
        self.indent = indent
        self.attr = {}
        self.parent = parent
        self.nodes = []

    def out(self):
        print('%s<%s%s>' % (
            (self.indent * ' '),
            self.name, ''.join(
                ' %s="%s"' % (k, v) for k, v in self.attr.items())))
        for node in self.nodes:
            node.out()
        print('%s</%s>' % ((self.indent * ' '), self.name))


class Leaf(object):
    def __init__(self, text, indent):
        self.indent = indent
        self.text = text

    def out(self):
        print((' ' * self.indent) + self.text)


class Htil(object):
    def __init__(self, source):
        self.file_indent = None
        self.source = source
        self.pos = 0
        self.row = 0
        self.col = 0

        self.indent = 0
        self.last_indent = 0
        self.state = 'lf'
        self.stack = []
        self.char = None
        self.attr = None
        self.node = self.root = Root()

    def read_until(self, until, bt=False):
        name = ''
        while self.pos < len(self.source) - 1 and not until(self.char):
            name += self.char
            self.pos += 1
            self.char = self.source[self.pos]
        if bt:
            self.pos -= 1
        return name

    def get_indent(self):
        return len(self.read_until(lambda c: c != ' ', True))

    def process(self):
        assert self.get_indent() == 0

        while self.pos < len(self.source) - 1:
            self.pos += 1
            self.char = self.source[self.pos]

            if self.char == ' ':
                pass
            elif self.char == '\n':
                self.pos += 1
                if self.pos == len(self.source):
                    break
                self.char = self.source[self.pos]
                self.last_indent = self.indent
                self.indent = self.get_indent()
                if self.file_indent is None:
                    self.file_indent = self.indent
                if self.state in 'tag' and self.indent < self.last_indent:
                    for i in range((self.last_indent - self.indent) //
                                   self.file_indent):
                        self.node = self.node.parent

                self.state = 'lf'
            elif self.char.isalnum():
                if self.state == 'lf':
                    name = self.read_until(lambda c: not c.isalnum(), True)
                    node = Node(name, self.indent, self.node)
                    self.node.nodes.append(node)
                    self.node = node
                    self.state = 'tag'
                elif self.state == 'tag':
                    name = self.read_until(lambda c: c == '=')
                    self.attr = name
                    self.state = 'attr_key'
                elif self.state == 'attr_key':
                    name = self.read_until(lambda c: c == ' ', True)
                    self.node.attr[self.attr] = name
                    self.attr = None
                    self.state = 'tag'
            elif self.char in '\'"':
                delim = self.char
                self.pos += 1
                self.char = self.source[self.pos]
                name = self.read_until(lambda c: c == delim)
                if self.state == 'attr_key':
                    self.node.attr[self.attr] = name
                    self.attr = None
                else:
                    self.node.nodes.append(Leaf(name, self.indent))
                self.state = 'tag'

    def html(self):
        self.process()
        self.root.out()


with open(sys.argv[1], 'r') as f:
    Htil(f.read()).html()
