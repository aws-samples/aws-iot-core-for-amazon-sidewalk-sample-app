from discovery import DiscoveryControl
from power_control import PowerControl
from report_state import ReportState

from utils import *
import logging
import json
from response import AlexaResponse

logger = logging.getLogger()
if logger.handlers:
	for handler in logger.handlers:
		logger.removeHandler(handler)
logging.basicConfig(format='%(asctime)s %(message)s', level=logging.ERROR)

def lambda_handler(event, context):

	if 'directive' not in event:
		logger.error("Missing key: directive, Is the request a valid Alexa Directive?")
		return False

	#logger.info(json.dumps(event))
	name = event['directive']['header']['name']
	namespace = event['directive']['header']['namespace']

	if namespace == 'Alexa.Authorization':
		logger.info("Authorization Request")
		if name == 'AcceptGrant':
			res_acceptgrant = AlexaResponse(namespace=namespace, name='AcceptGrant.Response')
			return res_acceptgrant.get()

	elif namespace == 'Alexa.Discovery':
		if name == 'Discover':
			logger.info("Discovery Request")
			discovery = DiscoveryControl(event, namespace)
			alexa_response=discovery.get_discovery_response()

			return alexa_response
	elif namespace == 'Alexa.PowerController':
		logger.info("PowerController Request")
		power_control = PowerControl()
		alexa_response=power_control.execute_power_control(event, namespace, name)

		return alexa_response
	elif namespace == 'Alexa':
		if name == 'ReportState':
			logger.info("ReportState Request")
			report_state = ReportState()
			alexa_response=report_state.get_state_report(event)

			return alexa_response
		else:
			logger.error("Unsupported operation")
			return False