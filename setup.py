from os import path

from setuptools import setup, find_packages

import netdev

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

# @formatter:off
setup(
    name='netdev',
    version=netdev.__version__,
    packages=find_packages(),
    url='https://github.com/selfuryon/netdev',
    license='BSD License',
    author='Yakovlev Sergey',
    author_email='selfuryon@gmail.com',
    description='Async network devices interaction library',
    requires=['asyncssh>=1.5.3', 'pyyaml'],
    long_description=long_description,
    keywords='network automation',
    classifiers=[
        # 3 - Alpha
        # 4 - Beta
        # 5 - Production/Stable
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3.5',
        'Intended Audience :: System Administrators',
        'Topic :: System :: Networking',
      ],
)
