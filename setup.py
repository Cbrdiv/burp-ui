#!/usr/bin/env python
# coding: utf-8

import os
import os.path
import re
import sys

from subprocess import check_output
from distutils import log
from distutils.core import Command
from setuptools import setup, find_packages
from setuptools.command.develop import develop
from setuptools.command.sdist import sdist
from setuptools.command.install import install

ROOT=os.path.dirname(os.path.realpath(__file__))


class DevelopWithBuildStatic(develop):
    def install_for_development(self):
        self.run_command('build_static')
        return develop.install_for_development(self)


class SdistWithBuildStatic(sdist):
    def make_distribution(self):
        self.run_command('build_static')
        return sdist.make_distribution(self)


class BuildStatic(Command):
    user_options = []
    description = "Install bower dependencies"
    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        log.info("running [bower install]")
        try:
            check_output(['bower', 'install'], cwd=ROOT)
        except Exception as e:
            log.warn(str(e))


class CustomInstall(install):
    def run(self):
        self.run_command('build_static')
        install.run(self)

def readme():
    """
    Function used to skip the screenshots part
    """
    desc = ''
    cpt = 0
    skip = False
    with open('README.rst') as f:
        for l in f.readlines():
            if l.rstrip() == 'Screenshots':
                skip = True
            if skip:
                cpt += 1
            if cpt > 7:
                skip = False
            if skip:
                continue
            desc += l
    return desc

with open(os.path.join(os.path.dirname(__file__), 'burpui', '__init__.py')) as f:
    data = f.read()

    name = re.search("__title__ *= *'(.*)'", data).group(1)
    author = re.search("__author__ *= *'(.*)'", data).group(1)
    author_email = re.search("__author_email__ *= *'(.*)'", data).group(1)
    description = re.search("__description__ *= *'(.*)'", data).group(1)
    url = re.search("__url__ *= *'(.*)'", data).group(1)

with open('requirements.txt', 'r') as f:
    requires = [x.strip() for x in f if x.strip()]

with open('test-requirements.txt', 'r') as f:
    test_requires = [x.strip() for x in f if x.strip()]

datadir = os.path.join('share', 'burpui', 'etc')
contrib = os.path.join('share', 'burpui', 'contrib')

setup(
    name=name,
    version=open('VERSION').read().rstrip(),
    description=description,
    long_description=readme(),
    license=open('LICENSE').read(),
    author=author,
    author_email=author_email,
    url=url,
    keywords='burp web ui',
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'static': 'burpui/static/*',
        'templates': 'burpui/templates/*',
        'VERSION': 'burpui/VERSION',
    },
    entry_points={
        'console_scripts': [
            'burp-ui=burpui.__main__:server',
            'bui-agent=burpui.__main__:agent',
        ],
    },
    data_files=[
        (datadir, [os.path.join(datadir, 'burpui.sample.cfg')]),
        (datadir, [os.path.join(datadir, 'buiagent.sample.cfg')]),
        (os.path.join(contrib, 'centos'), ['contrib/centos/init.sh']),
        (os.path.join(contrib, 'debian'), ['contrib/debian/init.sh']),
        (os.path.join(contrib, 'gunicorn.d'), ['contrib/gunicorn.d/burp-ui']),
    ],
    install_requires=requires,
    extras_require={
        'ldap_authentication': ['ldap3']
    },
    tests_require=test_requires,
    classifiers=[
        'Framework :: Flask',
        'Intended Audience :: System Administrators',
        'Natural Language :: English',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: System :: Archiving :: Backup',
        'Topic :: System :: Monitoring',
    ],
    cmdclass={
        'build_static': BuildStatic,
        'develop': DevelopWithBuildStatic,
        'sdist': SdistWithBuildStatic,
        'install': CustomInstall,
    }
)
