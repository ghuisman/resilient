#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name='rc_servicenow',
    version='1.0.0',
    license='IBM',
    author='Arama Tech',
    author_email='gert.huisman@aramatech.com',
    description="Resilient Circuits Components for 'rc_servicenow'",
    long_description="Resilient Circuits Components for 'rc_servicenow'",
    install_requires=[
        'resilient_circuits>=30.0.0'
    ],
    packages=find_packages(),
    include_package_data=True,
    platforms='any',
    classifiers=[
        'Programming Language :: Python',
    ],
    entry_points={
        "resilient.circuits.components": [
            "ServicenowTicketActionComponent = rc_servicenow.components.servicenow_ticket:ActionComponent"
        ],
        "resilient.circuits.configsection": ["gen_config = rc_servicenow.util.config:config_section_data"],
        "resilient.circuits.customize": ["customize = rc_servicenow.util.customize:customization_data"]
    }
)