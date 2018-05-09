import os
from setuptools import setup, find_packages


excluded_packages = ["tests",
                     "tests.*",
                     "examples",
                     "examples.*"
                     ]


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


def parse_requirements(filename):
    with open(filename) as f:
        required = f.read().splitlines()
    return required


setup(name = 'alchemist_lib',
      version = '1.0',
      description = 'Automatic trading library for cryptocurrencies.',
      long_description = read("README.rst"),
      url = 'https://github.com/Dodo33/alchemist-lib',
      author = 'Carniel Giorgio',
      author_email = 'dodo.33@gmx.com',
      python_requires = '>=3',
      license = "MIT",
      classifiers = [
          #https://pypi.python.org/pypi?%3Aaction=list_classifiers
          
          "Development Status :: 4 - Beta",
          "License :: OSI Approved :: MIT License",
          "Natural Language :: English",
          "Operating System :: OS Independent",
          "Programming Language :: Python :: 3.5",
          "Topic :: Office/Business :: Financial :: Investment",
          "Topic :: Scientific/Engineering :: Information Analysis"
          ],
      entry_points = {
        'console_scripts': [
            'alchemist = alchemist_lib.__main__:main',
        ],
      },
      packages = find_packages(exclude = excluded_packages),
      install_requires = parse_requirements("requirements.txt")
     )
