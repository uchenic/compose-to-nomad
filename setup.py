from setuptools import setup

import os

setup(name='ComposeNomadConvertor',
      version='0.0.3',
      description='Docker Compose to Nomad job convertor',
      author='Uchenic',
      author_email='uchenic@protonmail.com',
      url='',
      packages=['composenomadconvertor'],
      dependency_links=['git+https://github.com/uchenic/compose-ref.git@python_lib#egg=composeparser'],
      install_requires=['pyyaml'],
      scripts=['composenomadconvertor/nomadgen']
     )
