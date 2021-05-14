from setuptools import setup

import os

setup(name='ComposeNomadConvertor',
      version='0.0.3',
      description='Docker Compose to Nomad job convertor',
      author='Uchenic',
      author_email='uchenic@protonmail.com',
      url='',
      packages=['composenomadconvertor'],
      install_requires=['pyyaml', 'ComposeParser'],
      scripts=['composenomadconvertor/nomadgen']
     )
