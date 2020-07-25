from setuptools import setup
import os, io

from oneprint import __version__

here = os.path.abspath(os.path.dirname(__file__))
README = io.open(os.path.join(here, 'README.md'), encoding='UTF-8').read()
CHANGES = io.open(os.path.join(here, 'CHANGES.md'), encoding='UTF-8').read()
setup(name="oneprint",
      version=__version__,
      keywords=('oneprint', 'print', 'xprint', 'escpos'),
      description="A Uniform Print Library.",
      long_description=README + '\n\n\n' + CHANGES,
      long_description_content_type="text/markdown",
      url='https://github.com/sintrb/oneprint/',
      author="trb",
      author_email="sintrb@gmail.com",
      packages=['oneprint'],
      # install_requires=['requests', 'qrcode', 'pillow', 'pystrich', 'python-escpos'],
      zip_safe=False
      )
