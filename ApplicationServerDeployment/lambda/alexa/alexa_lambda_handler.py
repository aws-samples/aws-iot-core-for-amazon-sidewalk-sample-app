# Copyright 2023 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
"""
Handles requests from Alexa Smart Home Skill.
"""
import json
from discovery import DiscoveryControl
from power_control import PowerControl
from report_state import ReportState
import logging
from response import AlexaResponse

logger = logging.getLogger()
if logger.handlers:
	for handler in logger.handlers:
		logger.removeHandler(handler)
logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)


def lambda_handler(event, context):
	"""
	Handles requests from Alexa Smart Home Skill.
	"""
	if 'directive' not in event:
		logger.error("Missing key: directive, Is the request a valid Alexa Directive?")
		return False

	logger.info(json.dumps(event))
	name = event['directive']['header']['name']
	namespace = event['directive']['header']['namespace']
	alexa_response = None
	if namespace == 'Alexa.Authorization':
		logger.info("Authorization Request")
		if name == 'AcceptGrant':
			res_acceptgrant = AlexaResponse(namespace=namespace, name='AcceptGrant.Response')
			alexa_response = res_acceptgrant.get()

	elif namespace == 'Alexa.Discovery':
		if name == 'Discover':
			logger.info("Discovery Request")
			discovery = DiscoveryControl()
			alexa_response = discovery.get_discovery_response(event, namespace)

	elif namespace == 'Alexa.PowerController':
		logger.info("PowerController Request")
		power_control = PowerControl()
		alexa_response = power_control.execute_power_control(event, namespace, name)

	elif namespace == 'Alexa':
		if name == 'ReportState':
			logger.info("ReportState Request")
			report_state = ReportState()
			alexa_response = report_state.get_state_report(event)

		else:
			logger.error("Unsupported operation")
			return False

	logger.info(json.dumps(alexa_response))
	return alexa_response