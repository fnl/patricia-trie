from distutils.core import setup

setup(
    name='patricia-trie',
    version='1',
    description='A pure Python implementation of a PATRICIA trie.',
    license='Apache License v2',
    author='Florian Leitner',
    author_email='florian.leitner@gmail.com',
    url='http://www.github.com/fnl/patricia',
    py_modules=['patricia'],
    classifiers=[
        'Topic :: Software Development :: Libraries',
        'Intended Audience :: Developers',
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
    ]
)