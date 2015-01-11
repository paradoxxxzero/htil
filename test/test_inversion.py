import os
from htil import to_htil, to_html


def test_simple():
    with open(os.path.join(os.path.dirname(__file__), 'simple.htil')) as i:
        source = i.read()
    assert to_htil(to_html(source)) == source
    assert to_htil(to_html(to_htil(to_html(source)))) == source


def test_test():
    with open(os.path.join(os.path.dirname(__file__), 'test.htil')) as i:
        source = i.read()
    assert to_htil(to_html(
        to_htil(to_html(source)))) == to_htil(to_html(source))
