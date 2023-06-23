import os
import boto3
import requests
from response import AlexaResponse
import logging
import config
import utils
logger = logging.getLogger(__name__)
import logging
logger = logging.getLogger(__name__)
import time

class PowerControl(object):

	def execute_power_control(self, event, namespace, name):

		oauth_token, endpoint_id, correlation_token, cookie, payload = utils.transform_json_input(event)
		power_controller_response = AlexaResponse(correlationToken=correlation_token,
												  token=oauth_token,
												  endpointId=endpoint_id)

		is_device_online,device_id,current_states=utils.get_device_info()
		if is_device_online:
			power_controller_response.add_context_property(namespace='Alexa.EndpointHealth',
														   name='connectivity',
														   value={"value": config.CONNECTIVITY_ONLINE},
														   uncertaintyInMilliseconds=200)

			power_state_value = 'OFF' if name == 'TurnOff' else 'ON'
			status=utils.change_device_state(device_id,endpoint_id, power_state_value)
			if status:
				power_controller_response.add_context_property(namespace=namespace,
															   name='powerState',
															   value=power_state_value,
															   uncertaintyInMilliseconds=200)
			else:
				logger.error('BRIDGE_UNREACHABLE: ' + str(endpoint_id))
				logger.error(event)
				return utils.get_bridge_offline_response(oauth_token, endpoint_id)

			return power_controller_response.get()

		else:
			logger.error('BRIDGE_UNREACHABLE: ' + str(endpoint_id))
			logger.error(event)
			return utils.get_bridge_offline_response(oauth_token, endpoint_id)