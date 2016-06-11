import os
from distutils.core import setup

import netdev

README = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

setup(name='netdev', version=netdev.__version__, packages=['netdev', 'netdev.hp', 'netdev.cisco'], url='',
      license='BSD License', author='Yakovlev Sergey', author_email='selfuryon@gmail.com',
      description='Async network devices interaction library', requires=['asyncssh', 'yaml'])
