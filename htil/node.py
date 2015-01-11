from collections import OrderedDict
from .util import void_tags


class Root(object):
    def __init__(self):
        self.nodes = []
        self.parent = None

    def html(self, indent=2):
        return ''.join(node.html(0, indent) for node in self.nodes)

    def htil(self, indent=2):
        return ''.join(node.htil(0, indent) for node in self.nodes)


class Node(object):
    def __init__(self, name, attrs, parent):
        self.name = name
        self.attrs = attrs
        self.parent = parent
        self.nodes = []

    def html(self, level, indent):
        return ''.join(
            ('%s<%s%s%s>\n' % (
                level * ' ',
                self.name,
                ''.join(' %s="%s"' % (k, v) if v is not None else ' %s' % k
                        for k, v in self.attrs.items()),
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
        if self.attrs.get('id', None):
            tag = '%s#%s' % (tag, self.attrs['id'])
        if self.attrs.get('class', None):
            tag = '%s%s' % (tag, ''.join(
                '.%s' % c for c in self.attrs['class'].split(' ')))
        return '%s%s' % (tag, ''.join(
            ' %s="%s"' % (k, v) if v is not None else ' %s' % k
            for k, v in self.attrs.items()
            if k not in ('id', 'class')))

    def __repr__(self):
        return '<%s>' % self.tag()


class Leaf(object):
    def __init__(self, data, parent):
        self.parent = parent
        self.data = data
        self.nodes = ()

    def html(self, level, indent):
        return '%s%s\n' % ((' ' * level), self.data)

    def htil(self, level, indent):
        return '%s"%s"\n' % (
            (' ' * level), self.data
            .replace('\\', '\\\\')
            .replace('"', '\\"'))

    def __repr__(self):
        return '<%s data: %s>' % (repr(self.parent), self.data)
