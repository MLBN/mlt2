# -*- coding: utf-8 -*-
from setuptools import setup,find_packages

setup(name='mlt2',
      version='0.0.1',
      license='MITApache 2.0',
      author='Matthias Lesch',
      author_email='ml@matthiaslesch.de',
      description='A simple text processing tool to mix freely text and python code',
      include_package_data=True,
      packages=['mlt2'],
      #packages=find_packages(),
      #scripts=['scripts/pnw','scripts/ltsj'],
      platforms='any',
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 3',
          'License :: OSI Approved :: MIT License', 
          ],
      python_requires='>=3.5',
      )

