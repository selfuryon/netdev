from os import path

from setuptools import setup, find_packages

# from .netdev.version import __author__, __author_email__, __url__, __version__

base_dir = path.abspath(path.dirname(__file__))

with open(path.join(base_dir, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

with open(path.join(base_dir, 'netdev', 'version.py')) as version:
    exec(version.read())

# @formatter:off
setup(
    name='netdev',
    version=__version__,
    packages=find_packages(),
    url=__url__,
    license='BSD License',
    author=__author__,
    author_email=__author_email__,
    description='Asynchronous multi-vendor library for interacting with network devices',
    install_requires=['asyncssh>=1.6.2', 'pyyaml'],
    long_description=long_description,
    keywords='network automation',
    classifiers=[
        # 3 - Alpha
        # 4 - Beta
        # 5 - Production/Stable
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Intended Audience :: System Administrators',
        'Topic :: System :: Networking',
      ],
)
