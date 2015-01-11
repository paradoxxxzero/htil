from collections import OrderedDict
from .util import void_tags


class Root(object):
    def __init__(self):
        self.nodes = []
        self.parent = self

    def html(self, indent=2):
        return ''.join(node.html(0, indent) for node in self.nodes)

    def htil(self, indent=2):
        return ''.join(node.htil(0, indent) for node in self.nodes)


class Node(object):
    def __init__(self, name, parent):
        id = ''
        cls = []

        if '#' in name:
            name, id = name.split('#')

        if '.' in name:
            parts = name.split('.')
            name = parts[0]
            cls.extend(parts[1:])

        if '.' in id:
            parts = id.split('.')
            id = parts[0]
            cls.extend(parts[1:])

        self.attr = OrderedDict()
        if id:
            self.attr['id'] = id
        if cls:
            self.attr['class'] = ' '.join(cls)
        self.name = name
        self.parent = parent
        self.nodes = []

    def html(self, level, indent):
        return ''.join(
            ('%s<%s%s%s>\n' % (
                level * ' ',
                self.name,
                ''.join(' %s="%s"' % (k, v) for k, v in self.attr.items()),
                ' /' if self.name in void_tags else ''),
             ''.join(
                 node.html(level + indent, indent)
                 for node in self.nodes),
             '%s</%s>\n' % ((level * ' '), self.name)
             if self.name not in void_tags else ''))

    def htil(self, level, indent):
        return ''.join((
            '%s%s\n' % (
                level * ' ',
                self.tag()
            ),
            ''.join(
                node.htil(level + indent, indent) for node in self.nodes)))

    def tag(self):
        tag = self.name
        if self.attr.get('id', None):
            tag = '%s#%s' % (tag, self.attr['id'])
        if self.attr.get('class', None):
            tag = '%s%s' % (tag, ''.join(
                '.%s' % c for c in self.attr['class'].split(' ')))
        return '%s%s' % (tag, ''.join(
            ' %s="%s"' % (k, v) for k, v in self.attr.items()
            if k not in ('id', 'class')))

    def __repr__(self):
        return self.tag()


class Leaf(object):
    def __init__(self, text, parent):
        self.parent = parent
        self.text = text
        self.nodes = ()

    def html(self, level, indent):
        return '%s%s\n' % ((' ' * level), self.text)

    def htil(self, level, indent):
        return '%s"%s"\n' % ((' ' * level), self.text)
