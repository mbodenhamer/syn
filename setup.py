import os
from setuptools import setup, find_packages

DIR = os.path.dirname(os.path.abspath(__file__))

def read(fpath):
    with open(fpath, 'r') as f:
        return f.read()

def requirements(fpath):
    return list(filter(bool, read(fpath).split('\n')))

def version(fpath):
    return read(fpath).strip()

setup(
    name = 'syn',
    version = version('version.txt'),
    author = 'Matt Bodenhamer',
    author_email = 'mbodenhamer@mbodenhamer.com',
    description = 'Python metaprogramming, typing, and compilation facilities.',
    long_description = read('README.rst'),
    url = 'https://github.com/mbodenhamer/syn',
    packages = find_packages(),
    install_requires = requirements('requirements.txt'),
    namespace_packages = ['syn'],
)
