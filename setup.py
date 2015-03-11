import sys

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand


class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = ['--doctest-modules', '-v']

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


setup(
    name='turing_machine',
    version=1.0,
    url='https://github.com/dimazest/turing_machine',
    author="Dmitrijs Milajevs",
    author_email="dimazest@gmail.com",
    description='Turing Machine as a Python Generator.',
    long_description=open("README.rst").read(),
    license='MIT',
    py_modules=('turing_machine',),
    package_data={'': [
            'LICENSE',
            'README.rst',
            'Turing machine.ipynb',
        ]
    },
    # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
    ],
    zip_safe=False,
    tests_require=['pytest'],
    cmdclass={'test': PyTest},
)
