# Copyright 2023 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
from response import AlexaResponse
import logging
import config
import utils
from sidewalk_api import SidewalkApi

logger = logging.getLogger(__name__)


class ReportState(object):
	"""
	Handles ReportState directive requests
	"""

	def get_state_report(self, event):
		"""
		Handles ReportState directive requests
		"""
		sidewalk_app_api = SidewalkApi()
		is_device_online, device_id, current_states = sidewalk_app_api.get_device_info()
		global r_final_value, r_name, r_namespace
		oauth_token, endpoint_id, correlation_token, cookie, payload = utils.transform_json_input(event)

		report_state_response = AlexaResponse(correlationToken=correlation_token,
											  token=oauth_token,
											  endpointId=endpoint_id,
											  name="StateReport"
											  )
		if is_device_online:
			endpoint_connectivity = config.CONNECTIVITY_ONLINE if is_device_online else config.CONNECTIVITY_OFFLINE
			report_state_response.add_context_property(namespace='Alexa.EndpointHealth',
													   name='connectivity',
													   value={"value": endpoint_connectivity},
													   uncertaintyInMilliseconds=200)

			oem_model = cookie['oemModel']
			properties = []
			if oem_model in config.LIGHT_MODELS:
				leds_on = current_states['led_on']
				if int(endpoint_id) in leds_on:
					is_power_on = 1
				else:
					is_power_on = 0
				properties.append({"power": is_power_on})
			# Alexa does not support temperature sensor without ThermostatController interface so we are not adding temperature sensor for now
			# if oem_model in config.SENSOR_MODELS:
			# 	properties.append({"temp": sidewalk_app_api.get_device_temp(device_id)})

			for prop_name in properties:
				for key, value in prop_name.items():
					report_state_response = self.create_report_entry(value, key,
																	 report_state_response)
			return report_state_response.get()

		else:
			logger.error('DEVICE_OFFLINE_ERROR: ' + str(endpoint_id))
			logger.error(event)
			return utils.get_bridge_offline_response(oauth_token, endpoint_id)

	def create_report_entry(self, current_latest_value, prop_name, report_state_resp):
		"""
		Creates report entry for the given property as defined in the payload for ReportState directive
		"""
		additonal_info = None
		if current_latest_value is None:
			return report_state_resp

		global r_final_value, r_name, r_namespace, instance_name
		if prop_name == "power":
			r_namespace = 'Alexa.PowerController'
			r_name = 'powerState'
			r_final_value = 'ON' if current_latest_value else 'OFF'
			additonal_info = False

		elif prop_name == "temp":
			r_namespace = 'Alexa.TemperatureSensor'
			r_final_value = current_latest_value
			r_name = 'temperature'
			primary_property_name = 'value'
			addl_prop_name, addl_prop_value = 'scale', 'CELSIUS'
			additonal_info = True

		if additonal_info:
			report_state_resp.add_context_property(namespace=r_namespace,
												   name=r_name,
												   value={primary_property_name: r_final_value,
														  addl_prop_name: addl_prop_value},
												   uncertaintyInMilliseconds=200)
		else:
			report_state_resp.add_context_property(namespace=r_namespace,
												   name=r_name,
												   value=r_final_value,
												   uncertaintyInMilliseconds=200)
		return report_state_resp
