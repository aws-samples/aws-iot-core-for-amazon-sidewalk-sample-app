# Copyright 2023 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
import random
import uuid
import datetime
import logging

logger = logging.getLogger(__name__)


class AlexaResponse:
	"""
	Tranforms the final response to the Alexa Smart Home Skill expected JSON format
	"""
	def get_utc_timestamp(seconds=None):
		"""
		:param seconds: seconds to add to the current time
		:return: ISO formatted timestamp
		"""
		return str(datetime.datetime.utcnow().isoformat())[:-3] + 'Z'

	def __init__(self, **kwargs):
		"""
		:param kwargs: namespace, name, payload_version, token, endpointId, payload, correlationToken

		"""
		logger.info(kwargs)
		self.context_properties = []
		self.payload_endpoints = []
		self.payload_properties = []
		self.configuration = []

		self.context = {}
		self.event = {
			'header': {
				'namespace': kwargs.get('namespace', 'Alexa'),
				'name': kwargs.get('name', 'Response'),
				'messageId': str(uuid.uuid4()),
				'payloadVersion': kwargs.get('payload_version', '3')
			},
			'endpoint': {
				"scope": {
					"type": "BearerToken",
					"token": kwargs.get('token', 'INVALID')
				},
				"endpointId": kwargs.get('endpointId', 'INVALID')
			},
			'payload': kwargs.get('payload', {})
		}

		if 'correlationToken' in kwargs:
			self.event['header']['correlationToken'] = kwargs.get('correlationToken', 'INVALID')

		if 'cookie' in kwargs:
			logger.info('cookie')
			self.event['endpoint']['cookie'] = kwargs.get('cookie', '{}')

		if self.event['header']['name'] == 'AcceptGrant.Response' or self.event['header'][
			'name'] == 'Discover.Response':
			self.event.pop('endpoint')

	def add_payload_property(self, **kwargs):
		"""
		:param kwargs: namespace, name, value, uncertaintyInMilliseconds
		:return:
		"""
		self.payload_properties.append(self.create_payload_property(**kwargs))
	def create_payload_property(self, **kwargs):
		"""
		:param kwargs: namespace, name, value, uncertaintyInMilliseconds
		:return:
		"""
		return {
			"namespace": kwargs.get('namespace', 'Alexa.EndpointHealth'),
			'name': kwargs.get('name', 'connectivity'),
			"value": kwargs.get('value', {'value': 'OK'}),
			'timeOfSample': self.get_utc_timestamp(),
			'uncertaintyInMilliseconds': kwargs.get('uncertaintyInMilliseconds', 0)

		}

	def add_context_property(self, **kwargs):
		"""
		:param kwargs: namespace, name, value, uncertaintyInMilliseconds
		:return:
		"""
		self.context_properties.append(self.create_context_property(**kwargs))

	def add_cookie(self, key, value):
		"""
		:param key:
		:param value:
		:return:
		"""

		if "cookies" in self is None:
			self.cookies = {}

		self.cookies[key] = value

	def add_payload_endpoint(self, **kwargs):
		"""
		:param kwargs: capabilities, description, display_categories, endpoint_id, friendly_name, manufacturer_name
		:return:
		"""
		self.payload_endpoints.append(self.create_payload_endpoint(**kwargs))

	def create_context_property(self, **kwargs):
		"""
		:param kwargs: namespace, name, value, uncertaintyInMilliseconds
		:return:
		"""
		context_property = {
			'namespace': kwargs.get('namespace', 'Alexa.EndpointHealth'),
			'name': kwargs.get('name', 'connectivity'),
			'value': kwargs.get('value', {'value': 'OK'}),
			'timeOfSample': self.get_utc_timestamp(),
			'uncertaintyInMilliseconds': kwargs.get('uncertaintyInMilliseconds', 0)
		}

		instance = kwargs.get('instance', '')
		if instance is not None and len(instance) > 0:
			context_property['instance'] = instance

		return context_property

	def create_payload_endpoint(self, **kwargs):
		"""
		:param kwargs: capabilities, description, display_categories, endpoint_id, friendly_name, manufacturer_name
		:return:
		"""
		endpoint = {
			'capabilities': kwargs.get('capabilities', []),
			'description': kwargs.get('description', 'Sidewalk Smart Device'),
			'displayCategories': kwargs.get('display_categories', ['OTHER']),
			'endpointId': kwargs.get('endpoint_id', 'endpoint_' + "%0.6d" % random.randint(0, 999999)),
			'friendlyName': kwargs.get('friendly_name', 'Sidewalk Smart Device'),
			'manufacturerName': kwargs.get('manufacturer_name', 'Sidewalk')
		}

		if 'cookie' in kwargs:
			endpoint['cookie'] = kwargs.get('cookie', {})

		if 'additional_attributes' in kwargs:
			endpoint['additionalAttributes'] = kwargs.get('additional_attributes', {})

		if 'connections' in kwargs:
			endpoint['connections'] = kwargs.get('connections', [])
		return endpoint

	def create_payload_endpoint_capability(self, **kwargs):
		"""
		:param kwargs: type, interface, version, instance, supported, capability_resources, friendly_names, configuration, supports_deactivation
		:return:
		"""
		capability = {
			'type': kwargs.get('type', 'AlexaInterface'),
			'interface': kwargs.get('interface', 'Alexa'),
			'version': kwargs.get('version', '3')
		}
		supported = kwargs.get('supported', None)
		instance = kwargs.get('instance', None)
		capability_resources = kwargs.get('capability_resources', None)
		friendly_names = kwargs.get('friendly_names', None)
		configuration = kwargs.get('configuration', None)
		supports_deactivation = kwargs.get('supports_deactivation', None)
		if instance:
			capability['instance'] = instance

		if supported:
			capability['properties'] = {}
			capability['properties']['supported'] = supported
			capability['properties']['proactivelyReported'] = kwargs.get('proactively_reported', True)
			capability['properties']['retrievable'] = kwargs.get('retrievable', True)

		if capability_resources:
			capability['capabilityResources'] = kwargs.get('capability_resources', {})

		if friendly_names:
			if 'capabilityResources' not in capability:
				capability['capabilityResources'] = {}
			capability['capabilityResources']['friendlyNames'] = friendly_names
		if configuration:
			capability['configuration'] = configuration
		if supports_deactivation:
			capability['supportsDeactivation'] = supports_deactivation

		return capability

	def get(self, remove_empty=True):
		"""
		:param remove_empty:
		:return: response dict with context and event
		"""
		response = {
			'context': self.context,
			'event': self.event
		}

		if len(self.context_properties) > 0:
			response['context']['properties'] = self.context_properties

		if len(self.payload_endpoints) > 0:
			response['event']['payload']['endpoints'] = self.payload_endpoints

		if len(self.payload_properties) > 0:
			response['event']['payload']['change']['properties'] = self.payload_properties

		if remove_empty:
			if len(response['context']) < 1:
				response.pop('context')

		return response

	def set_payload(self, payload):
		"""
		:param payload:
		:return:
		"""
		self.event['payload'] = payload

	def set_payload_endpoint(self, payload_endpoints):
		"""
		:param payload_endpoints:
		:return:
		"""
		self.payload_endpoints = payload_endpoints

	def set_payload_endpoints(self, payload_endpoints):
		"""
		:param payload_endpoints:
		:return:
		"""
		if 'endpoints' not in self.event['payload']:
			self.event['payload']['endpoints'] = []
		self.event['payload']['endpoints'] = payload_endpoints
