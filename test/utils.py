from htil import to_htil, to_html, Html


def iso_html(html):
    return Html(html).html() == Html(Html(html).html()).html()


def iso_html_htil(html):
    return Html(html).html() == to_html(to_htil(html))


def iso_processing(html):
    return Html(html).html() == to_html(to_htil(html))
