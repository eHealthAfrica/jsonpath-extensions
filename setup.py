#!/usr/bin/env python

# Copyright (C) 2018 by eHealth Africa : http://www.eHealthAfrica.org
#
# See the NOTICE file distributed with this work for additional information
# regarding copyright ownership.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

from datetime import datetime
from io import open
import os
from setuptools import setup, find_packages


def read(f):
    return open(f, 'r', encoding='utf-8').read()


VERSION = os.environ.get('VERSION', str(datetime.now().isoformat()) + '-alpha')

setup(
    version=VERSION,
    name='eha_jsonpath',
    description='jsonpath_ng with extended functionality',
    long_description=read('README.md'),
    long_description_content_type='text/markdown',

    url='https://github.com/eHealthAfrica/jsonpath-extensions/',
    author='eHealth Africa',
    author_email='aether@ehealthafrica.org',
    license='Apache2 License',

    install_requires=[
        'jsonpath-ng',
    ],
    setup_requires=['pytest-runner'],
    tests_require=['pytest', 'pytest-cov'],

    packages=find_packages(),
    include_package_data=False,
)
