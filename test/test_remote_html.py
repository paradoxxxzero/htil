from .utils import iso_html, iso_html_htil, iso_processing
from urllib.request import urlopen


def test_google():
    with urlopen('http://google.com/') as s:
        source = s.read().decode('latin-1')
    assert iso_html(source)
    assert iso_html_htil(source)
    assert iso_processing(source)


def test_reddit():
    with urlopen('http://reddit.com/') as s:
        source = s.read().decode('utf-8')
    assert iso_html(source)
    assert iso_html_htil(source)
    assert iso_processing(source)
