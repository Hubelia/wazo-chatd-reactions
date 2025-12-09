#!/usr/bin/env python3
# Copyright 2024 Community Contributors
# SPDX-License-Identifier: GPL-3.0-or-later

from setuptools import find_packages, setup

import yaml

with open('wazo/plugin.yml') as f:
    metadata = yaml.safe_load(f)

setup(
    name=metadata['name'],
    version=metadata['version'],
    description=metadata.get('description', metadata['display_name']),
    author=metadata['author'],
    url=metadata.get('homepage', ''),
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'wazo_chatd_reactions': ['api.yml'],
    },
    entry_points={
        'wazo_chatd.plugins': [
            'reactions = wazo_chatd_reactions.plugin:Plugin',
        ],
    },
)
