import os
from setuptools import setup, find_packages

DIR = os.path.dirname(os.path.abspath(__file__))

def requirements(fpath):
    with open(fpath, 'r') as f:
        txt = f.read()
    reqs = list(filter(bool, txt.split('\n')))
    return reqs

setup(
    name = 'syn',
    version = '0.0.1',
    author = 'Matt Bodenhamer',
    author_email = 'mbodenhamer@mbodenhamer.com',
    description = 'Python metaprogramming, typing, and compilation facilities.',
    packages = find_packages(),
    install_requires = requirements('requirements.txt'),
)
