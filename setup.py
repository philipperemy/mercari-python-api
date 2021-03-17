from setuptools import find_packages
from setuptools import setup

setup(
    name='mercari-python',
    version='0.4',
    author='Philippe Remy',
    packages=find_packages(),
    install_requires=[
        'mailthon',
        'requests',
        'beautifulsoup4',
        'lxml',
        'wget'
    ]
)
