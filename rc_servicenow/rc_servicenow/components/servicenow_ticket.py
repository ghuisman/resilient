#!/usr/bin/python2.7
"""Create ServiceNow Ticket.

This component creates a ticket on ServiceNow, triggered when certain
requirements are met on Resilient itself

Attributes
----------
LOG : string
    Logsettings
CONFIG_DATA_SECTION : string
    Get config(?)
"""

import requests
import logging
import json
import uuid
from circuits.core.handlers import handler
from resilient_circuits.actions_component import ResilientComponent
from resilient_circuits.actions_component import ActionMessage

LOG = logging.getLogger(__name__)
CONFIG_DATA_SECTION = 'rc_servicenow'

class ActionComponent(ResilientComponent):
    """Create ServiceNow Ticket."""

    def __init__(self, opts):
        """Load config and start logging on initalization."""
        super(ActionComponent, self).__init__(opts)
        self.options = opts.get(CONFIG_DATA_SECTION, {})
        LOG.debug(self.options)

        self.channel = "actions." + self.options.get("queue", "inc_test")

    @handler('create_sn_ticket')
    def _actionComponent(self, event, *args, **kwargs):
        """Create function for snow ticket handling.

        Currently does not use any of it's parameters,
        will be updated when its more apparent.

        Parameters
        ----------
        event : {[type]}
            [description]
        *args : {[type]}
            [description]
        **kwargs : {[type]}
            [description]
        """
        if not isinstance(event, ActionMessage):
            return

        incident = event.message

        reference_number = str(uuid.uuid4())
        #inc_priority = incident['incident']['properties']['priority']

        headers = {"Content-Type": "application/json",
                   "Accept": "application/json"}

        testdata = {
            "action": "New",
            "company": incident['incident']['properties']['company_ticket_id'],
            "reference_number": reference_number,
            "short_description": 'short description of ticket',
            "description": incident['incident']['description'],
            "ci": 'Security Monitoring TS (Model)',
            "impact": incident['incident']['properties']['servicenow_impact'],
            "urgency": incident['incident']['properties']['servicenow_urgency']
        }

        response = requests.post(self.options.get('url'),
                                 auth=(self.options.get('username'), self.options.get('password')),
                                 headers=headers,
                                 json=testdata)

        def update_fn(incident):
            incident['properties']['servicenow_ticket_number'] = response['result']['ticket_number']
            incident['properties']['servicenow_reference_number'] = response['result']['reference_number']
            return incident

        print(response.json)
        response = response.json()

        self.rest_client().get_put("/incidents/{}".format(incident['incident']['id']), update_fn)

        yield "Ticket has been successfully created."
