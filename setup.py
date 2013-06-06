from distutils.core import setup
import patricia

with open('README.rst') as file:
    long_description = file.read()

setup(
    name='patricia-trie',
    version=patricia.__version__,
    description='A pure Python implementation of a PATRICIA trie.',
    long_description=long_description,
    license='Apache License v2',
    author='Florian Leitner',
    author_email='florian.leitner@gmail.com',
    url='http://www.github.com/fnl/patricia-trie',
    py_modules=['patricia'],
    classifiers=[
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Text Processing :: Indexing',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: Apache Software License',
    ]
)
