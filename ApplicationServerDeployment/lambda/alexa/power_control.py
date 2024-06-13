# Copyright 2023 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
from response import AlexaResponse
import logging
import config
import utils
from sidewalk_api import SidewalkApi
logger = logging.getLogger(__name__)


class PowerControl(object):
	"""
	Handles PowerController directive requests
	"""

	def execute_power_control(self, event, namespace, name):
		"""
		Evaluates and executes PowerController directive requests and provides response as per https://developer.amazon.com/docs/device-apis/alexa-powercontroller.html#response-format
		"""
		oauth_token, endpoint_id, correlation_token, cookie, payload = utils.transform_json_input(event)
		sidewalk_app_api=SidewalkApi()
		power_controller_response = AlexaResponse(correlationToken=correlation_token,
												  token=oauth_token,
												  endpointId=endpoint_id)

		is_device_online, device_id, current_states = sidewalk_app_api.get_device_info()
		if is_device_online:
			power_controller_response.add_context_property(namespace='Alexa.EndpointHealth',
														   name='connectivity',
														   value={"value": config.CONNECTIVITY_ONLINE},
														   uncertaintyInMilliseconds=200)

			power_state_value = 'OFF' if name == 'TurnOff' else 'ON'
			status = sidewalk_app_api.change_device_state(device_id, endpoint_id, power_state_value)
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

