from htil import Htil, Html, to_htil, to_html


def test_indent():
    assert to_html(
'''html
  head
  body
    section
      article
    section
      p
''') == (
'''<html>
  <head>
  </head>
  <body>
    <section>
      <article>
      </article>
    </section>
    <section>
      <p>
      </p>
    </section>
  </body>
</html>
''')
