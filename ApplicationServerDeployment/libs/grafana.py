# Copyright 2023 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import json
import requests


class Grafana:
    """Client for Grafana http api calls"""

    def __init__(self, ws_url, ws_api_key):
        """Creates Grafana http client.

        :param ws_url:      Workspace url.
        :param ws_api_key:  Workspace api key.
        """
        self.base_url = f'https://{ws_url}'
        self.headers = {
            'Authorization': f'Bearer {ws_api_key}',
            'Content-Type': 'application/json'
        }

    def refresh_api_key(self, ws_api_key):
        """Refreshes workspace api key.

        :param ws_api_key:  Workspace api key.
        """
        self.headers['Authorization'] = f'Bearer {ws_api_key}'

    def _post(self, endpoint, payload):
        """Sends POST request.

        :param endpoint:    Specific endpoint address.
        :param payload:     Payload dict.
        :return:            (status, response).
        """
        response = requests.post(self.base_url + endpoint, data=json.dumps(payload), headers=self.headers)
        return (True, response) if 200 <= response.status_code < 300 else (False, response)

    def _put(self, endpoint, payload):
        """Sends PUT request.

        :param endpoint:    Specific endpoint address.
        :param payload:     Payload dict.
        :return:            (status, response).
        """
        response = requests.put(self.base_url + endpoint, data=json.dumps(payload), headers=self.headers)
        return (True, response) if 200 <= response.status_code < 300 else (False, response)

    def _get(self, endpoint):
        """Sends GET request.

        :param endpoint:    Specific endpoint address.
        :return:            (status, response).
        """
        response = requests.get(self.base_url + endpoint, headers=self.headers)
        return (True, response) if 200 <= response.status_code < 300 else (False, response)

    def create_data_source(self, payload):
        """Adds data source to the Grafana workspace.

        :param payload:     Dict with the datasource payload.
        :return:            (status, response, datasource_uid).
        """
        status, response = self._post('/api/datasources', payload)
        if status:
            return status, response, json.loads(response.content)['datasource']['uid']
        else:
            return status, response, ''

    def get_data_source(self, name):
        """Get existing data source by name.

        :param name:    Datasource name.
        :return:        (status, response, datasource_uid).
        """
        status, response = self._get(f'/api/datasources/name/{name}')
        if status:
            return status, response, json.loads(response.content)['uid']
        else:
            return status, response, ''

    def create_dashboard(self, payload):
        """Adds dashboard to the Grafana workspace.

        :param payload:     Dict with the dashboard payload.
        :return:            (status, response, dashboard_id).
        """
        status, response = self._post('/api/dashboards/db', payload)
        if status:
            return status, response, json.loads(response.content)['id']
        else:
            return status, response, ''

    def update_org_preferences(self, payload):
        """Update organization preferences.

        :param payload:     Dict with the preferences payload.
        :return:            (status, response).
        """
        return self._put('/api/org/preferences', payload)
