# Copyright 2023 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
from response import AlexaResponse
import logging
import config
import utils
from sidewalk_api import SidewalkApi

logger = logging.getLogger(__name__)


class DiscoveryControl(object):
	"""
	Handles Discovery requests from Alexa Smart Home Skill.
	"""

	def get_discovery_response(self, event, namespace):
		"""
		Evaluates and executes Discovery directive request and returns a response as per https://developer.amazon.com/docs/device-apis/alexa-discovery.html#response-format
		"""
		discover_response = AlexaResponse(
			namespace=namespace, name='Discover.Response')
		device_oem_model = ""
		sidewalk_app_api = SidewalkApi()
		user_devices = sidewalk_app_api.get_user_devices()
		if len(user_devices) == 0:
			logger.error("No devices found for user")
			return discover_response.get()
		for device_wrapper in user_devices:
			for device in device_wrapper["led"]:
				if 'led' in device_wrapper and 'sensor' in device_wrapper:
					device_oem_model = config.DEVKIT_MODEL
				dsn = int(device)
				friendly_name = "Light " + " " + str(dsn)
				display_categories, capabilities = self.get_device_category_and_capabilities(discover_response,
																							 device_oem_model)
				discover_response.add_payload_endpoint(
					endpoint_id=dsn,
					manufacturer_name=config.DEVICE_MANUFACTURER,
					description=config.PRODUCT_DESCRIPTION,
					friendly_name=friendly_name,
					additional_attributes={
						'manufacturer': config.DEVICE_MANUFACTURER,
						'model': device_oem_model,
						'serialNumber': dsn,
						'firmwareVersion': '1.0.0',
						'softwareVersion': '1.0.0',
						'customIdentifier': dsn
					},
					display_categories=display_categories,
					cookie={'oemModel': device_oem_model},
					capabilities=capabilities,
					connections=[{'type': 'TCP_IP'}]
				)

		return discover_response.get()

	def get_device_category_and_capabilities(self, registration_response, oem_model):
		"""
		Generate the display categories and capabilities for a device as defined by Alexa Skills Kit API.
		"""
		display_categories = None
		capabilities = None
		capability_alexa = registration_response.create_payload_endpoint_capability()
		capability_alexa_endpoint_health = registration_response.create_payload_endpoint_capability(
			interface='Alexa.EndpointHealth',
			supported=[{'name': 'connectivity'}]
		)

		capability_alexa_power_controller = registration_response.create_payload_endpoint_capability(
			interface='Alexa.PowerController',
			supported=[{'name': 'powerState'}]
		)

		capability_alexa_temperature_sensor = registration_response.create_payload_endpoint_capability(
			interface='Alexa.TemperatureSensor',
			supported=[{'name': 'temperature'}]
		)

		if oem_model in config.LIGHT_MODELS:
			display_categories = ['LIGHT']
			capabilities = [capability_alexa,
							capability_alexa_power_controller,
							capability_alexa_temperature_sensor,
							capability_alexa_endpoint_health]

		return display_categories, capabilities
