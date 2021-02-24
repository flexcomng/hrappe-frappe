# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

with open('requirements.txt') as f:
	install_requires = f.read().strip().split('\n')

# get version from __version__ variable in hrapp/__init__.py
from hrapp import __version__ as version

setup(
	name='hrapp',
	version=version,
	description='HR Portal Plus Appraisal customization',
	author='Youssef Restom',
	author_email='youssef@totrox.com',
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
