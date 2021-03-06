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
import re
import requests
import logging
from circuits.core.handlers import handler
from resilient_circuits.actions_component import ResilientComponent
from resilient_circuits.actions_component import ActionMessage

LOG = logging.getLogger(__name__)
CONFIG_DATA_SECTION = 'rc_servicenow'
TAG_RE = re.compile(r'<[^>]+>')

class ActionComponent(ResilientComponent):
    """Create ServiceNow Ticket."""

    def __init__(self, opts):
        """Load config and start logging on initalization."""
        super(ActionComponent, self).__init__(opts)
        self.options = opts.get(CONFIG_DATA_SECTION, {})
        LOG.debug(self.options)

        self.channel = "actions." + self.options.get("queue")

    @handler('create_ticket')
    def createTicket(self, event, *args, **kwargs):
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

        reference_number = 'RS1-' + str(incident['incident']['org_id']) + '-' + str(incident['incident']['id'])

        def remove_tags(text):
            return TAG_RE.sub('', text)

        headers = {"Content-Type": "application/json",
                   "Accept": "application/json"}

        testdata = {
            "action": "New",
            "company": incident['incident']['properties']['company_ticket_id'],
            "reference_number": reference_number,
            "short_description": 'short description of ticket',
            "description": remove_tags(incident['incident']['description']),
            "ci": 'Security Monitoring TS (Model)',
            "impact": incident['incident']['properties']['servicenow_impact'],
            "urgency": incident['incident']['properties']['servicenow_urgency']
        }

        def update_fn(incident):
            incident['properties']['servicenow_ticket_number'] = response['result']['ticket_number']
            incident['properties']['servicenow_reference_number'] = response['result']['reference_number']
            return incident

        try:
            response = requests.post(self.options.get('url'),
                                     auth=(self.options.get('user'), self.options.get('password')),
                                     headers=headers,
                                     json=testdata)

            response = response.json()
            LOG.info(response)

            if response['result']['state'] == 'inserted' and 'Incident is created successfully' in response['result']['note']:
                self.rest_client().get_put("/incidents/{}".format(incident['incident']['id']), update_fn)
                yield 'Ticket has been successfully created.'
            elif(response['result']['state'] == 'error' and 'Duplicate' in response['result']['note']):
                yield 'A ticket for this incident already exists.'
            elif('No company found for company' in response['result']['note']):
                yield 'No company was found for ' + incident['incident']['properties']['company_ticket_id']
            elif('is not found or inactive' in response['result']['note']):
                yield 'CI ' + 'Security Monitoring TS (Model)' + 'is not found or inactive.'

        except (ValueError, KeyError, TypeError) as err:
            print(repr(err))
            return

    @handler('comment_ticket')
    def commentTicket(self, event, *args, **kwargs):

        if not isinstance(event, ActionMessage):
            return

        yield "Comment has been successfully added."

    @handler('resolve_ticket')
    def resolveTicket(self, event, *args, **kwargs):

        if not isinstance(event, ActionMessage):
            return

        yield "Ticket has been successfully resolved."

    @handler('reopen_ticket')
    def reopenTicket(self, event, *args, **kwargs):

        if not isinstance(event, ActionMessage):
            return

        yield "Ticket has been successfully reopened."

    @handler('close_ticket')
    def closeTicket(self, event, *args, **kwargs):

        if not isinstance(event, ActionMessage):
            return

        yield "Ticket has been successfully closed."