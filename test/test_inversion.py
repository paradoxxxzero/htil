from urllib.request import urlopen
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


def test_google():
    with urlopen('http://google.com/') as s:
        source = s.read().decode('latin-1')


def test_reddit():
    with urlopen('http://reddit.com/') as s:
        source = s.read().decode('utf-8')
    assert to_html(to_htil(
        to_html(to_htil(source)))) == to_html(to_htil(source))
