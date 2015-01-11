from html.parser import HTMLParser
from collections import OrderedDict
from .node import Root, Node, Leaf
from .util import void_tags


class Parser(object):
    def __init__(self, source):
        self.source = source
        self.node = self.root = Root()
        self.process()

    def html(self):
        return self.root.html()

    def htil(self):
        return self.root.htil()


class Htil(Parser):
    def __init__(self, source):
        self.file_indent = None
        self.pos = 0
        self.row = 1
        self.col = 1

        self.indent = 0
        self.last_indent = 0
        self.state = 'lf'
        self.attr = None
        super().__init__(source)

    def read_until(self, until, bt=False, drop_comments=True):
        name = ''
        escape = False
        while self.pos < len(self.source) - 1 and not (
                until(self.char) and not escape):
            if self.char == '\n':
                self.row += 1
            if drop_comments and self.char == '/' and self.next_char == '/':
                self.pos += 2
                self.col += 2
                self.read_until(lambda c: c == '\n')
                continue

            if self.char != '\\' or escape:
                name += self.char
                escape = False
            else:
                escape = self.char == '\\'
            self.pos += 1
            self.col += 1
        if bt:
            self.pos -= 1
            self.col -= 1
        return name

    def get_indent(self):
        return len(self.read_until(lambda c: c != ' ', True))

    @property
    def char(self):
        return self.source[self.pos]

    @property
    def next_char(self):
        return self.source[self.pos + 1] if self.pos < len(
            self.source) - 1 else None

    def process(self):
        assert self.get_indent() == 0

        while self.pos < len(self.source) - 1:
            self.pos += 1
            self.col += 1

            if self.char == ' ':
                pass
            elif self.char == '\n':
                self.new_line()
            elif self.char in '\'"':
                self.read_data()
            elif self.char == '/' and self.next_char == '/':
                self.pos += 2
                self.col += 2
                self.read_until(lambda c: c == '\n', True)
                continue
            elif self.state == 'lf':
                self.read_tag()
            elif self.state == 'tag':
                self.read_attr_key()
            elif self.state == 'attr_key':
                self.read_attr_value()

    def read_data(self):
        delim = self.char
        self.pos += 1
        self.col += 1
        name = self.read_until(lambda c: c == delim, False, False)
        if self.state == 'attr_key':
            self.node.attrs[self.attr] = name
            self.attr = None
        else:
            leaf = Leaf(name, self.node)
            self.node.nodes.append(leaf)
            self.node = leaf
        self.state = 'tag'

    def parse_tag(self, tag):
        attrs = OrderedDict()
        id = ''
        cls = []

        if '#' in tag:
            tag, id = tag.split('#')

        if '.' in tag:
            parts = tag.split('.')
            tag = parts[0]
            cls.extend(parts[1:])

        if '.' in id:
            parts = id.split('.')
            id = parts[0]
            cls.extend(parts[1:])
        if id:
            attrs['id'] = id
        if cls:
            attrs['class'] = ' '.join(cls)
        return tag, attrs

    def read_tag(self):
        tag = self.read_until(lambda c: c in ' \n', True)
        tag, attrs = self.parse_tag(tag)
        node = Node(tag, attrs, self.node)
        self.node.nodes.append(node)
        self.node = node
        self.state = 'tag'

    def read_attr_key(self):
        name = self.read_until(lambda c: c in '=\n', True)
        self.attr = name
        if self.next_char != '=':
            self.node.attrs[self.attr] = None
        else:
            self.pos += 1
        self.state = 'attr_key'

    def read_attr_value(self):
        name = self.read_until(lambda c: c in ' \n', True, False)
        self.node.attrs[self.attr] = name
        self.attr = None
        self.state = 'tag'

    def new_line(self):
        self.col = 1
        self.row += 1
        self.pos += 1
        indent = self.get_indent()
        if self.char == '\n':
            return
        self.last_indent = self.indent
        self.indent = indent
        if self.file_indent is None and self.indent:
            self.file_indent = self.indent
        if self.indent > self.last_indent and (
            self.indent - self.last_indent != self.file_indent) or (
                (self.last_indent - self.indent) % self.file_indent):
            raise IndentationError('Bad indent at %d:%d' % (
                self.row, self.col))

        if self.state in 'tag' and self.indent <= self.last_indent:
            for i in range(1 + (self.last_indent - self.indent) //
                           self.file_indent):
                self.node = self.node.parent
        self.state = 'lf'


class Html(Parser):
    def process(self):
        html = self

        class HtmlParser(HTMLParser):
            def ordered_attrs(self, attrs):
                attrs = OrderedDict(attrs)
                rv = OrderedDict()
                if 'id' in attrs:
                    rv['id'] = attrs['id']
                if 'class' in attrs:
                    rv['class'] = attrs['class']
                rv.update(attrs)
                return rv

            def handle_starttag(self, tag, attrs):
                if tag in void_tags:
                    self.handle_startendtag(tag, attrs)
                    return
                node = Node(tag, self.ordered_attrs(attrs), html.node)
                html.node.nodes.append(node)
                html.node = node

            def handle_startendtag(self, tag, attrs):
                node = Node(tag, self.ordered_attrs(attrs), html.node)
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


def to_htil(html):
    return Html(html).htil()


def to_html(htil):
    return Htil(htil).html()
