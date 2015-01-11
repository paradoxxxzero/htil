from html.parser import HTMLParser
from collections import OrderedDict
from .node import Root, Node, Leaf
from .util import void_tags


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
        escape = False
        while self.pos < len(self.source) - 1 and not (
                until(self.char) and not escape):
            if self.char != '\\' or escape:
                name += self.char
                escape = False
            else:
                escape = self.char == '\\'
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
                indent = self.get_indent()
                if self.char == '\n':
                    continue
                self.last_indent = self.indent
                self.indent = indent
                if self.file_indent is None:
                    self.file_indent = self.indent
                if self.state in 'tag' and self.indent <= self.last_indent:
                    for i in range(1 + (self.last_indent - self.indent) //
                                   self.file_indent):
                        self.node = self.node.parent
                self.state = 'lf'
            elif self.char in '\'"':
                delim = self.char
                self.pos += 1
                self.char = self.source[self.pos]
                name = self.read_until(lambda c: c == delim)
                if self.state == 'attr_key':
                    self.node.attr[self.attr] = name
                    self.attr = None
                else:
                    leaf = Leaf(name, self.node)
                    self.node.nodes.append(leaf)
                    self.node = leaf
                self.state = 'tag'
            else:
                if self.state == 'lf':
                    name = self.read_until(lambda c: c in ' \n', True)
                    node = Node(name, self.node)
                    self.node.nodes.append(node)
                    self.node = node
                    self.state = 'tag'
                elif self.state == 'tag':
                    name = self.read_until(lambda c: c == '=')
                    self.attr = name
                    self.state = 'attr_key'
                elif self.state == 'attr_key':
                    name = self.read_until(lambda c: c in ' \n', True)
                    self.node.attr[self.attr] = name
                    self.attr = None
                    self.state = 'tag'

    def html(self):
        self.process()
        return self.root.html()


class Html(object):
    def __init__(self, source):
        self.root = Root()
        self.source = source
        self.node = self.root

    def process(self):
        html = self

        class HtmlParser(HTMLParser):
            def handle_starttag(self, tag, attrs):
                if tag in void_tags:
                    self.handle_startendtag(tag, attrs)
                    return
                node = Node(tag, html.node)
                html.node.nodes.append(node)
                html.node = node
                html.node.attr = OrderedDict(attrs)

            def handle_startendtag(self, tag, attrs):
                node = Node(tag, html.node)
                node.attr = OrderedDict(attrs)
                html.node.nodes.append(node)

            def handle_data(self, data):
                data = data.strip(' \t\n\r')
                if data:
                    leaf = Leaf(data, html.node)
                    html.node.nodes.append(leaf)

            def handle_endtag(self, tag):
                if tag in void_tags:
                    return
                html.node = html.node.parent

        HtmlParser().feed(self.source)

    def htil(self):
        self.process()
        return self.root.htil()


def to_htil(html):
    return Html(html).htil()


def to_html(htil):
    return Htil(htil).html()
