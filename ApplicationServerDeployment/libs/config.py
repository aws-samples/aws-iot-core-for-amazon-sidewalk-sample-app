# Copyright 2023 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import yaml

from libs.user import User
from libs.utils import *


class Config:
    """
    Provides methods for reading and updating config files

    Attributes
    ----------
        aws_profile: str
            AWS profile name.
        sid_dest_name: str
            Sidewalk destination name.
        web_app_url: str
            Sensor Monitoring App URL
        identity_store_id: str
            ID of the identity store.
        identity_center_users: [User]
            List of identity center users.
        workspace_url: str
            Grafan workspace URL.
    """
    CONFIG_PATH = Path(__file__).resolve().parents[2].joinpath('config.yaml')
    CONFIG_GRAFANA_PATH = Path(__file__).resolve().parents[1].joinpath('config_grafana.yaml')

    def __init__(self):
        self._read_config()
        self._read_grafana_config()

    def set_web_app_url(self, url):
        """
        Sets web_app_url in both: object and config file.

        :param url:     Web App URL to be set.
        """
        self.web_app_url = url
        self._update_config(self.CONFIG_PATH, 'Outputs', 'WEB_APP_URL', url)

    def set_workspace_url(self, url):
        """
        Sets Grafana workspace_url in both: object and config file.

        :param url:     Grafana workspace URL to be set.
        """
        self.workspace_url = url
        self._update_config(self.CONFIG_GRAFANA_PATH, 'Outputs', 'WORKSPACE_URL', url)

    def _read_config(self):
        """
        Reads config file.
        """
        try:
            config = yaml.safe_load(read_file(self.CONFIG_PATH))
            self.aws_profile = config.get('Config', {}).get('AWS_PROFILE', 'default')
            self.sid_dest_name = config.get('Config', {}).get('DESTINATION_NAME', 'SidewalkDestination')
            self.region_name = 'us-east-1' # Leave this as us-east-1 unless you know what you are doing
            self.web_app_url = ''
        except yaml.YAMLError as e:
            terminate(f'Invalid structure of a config file: {e}', ErrCode.EXCEPTION)

    def _read_grafana_config(self):
        """
        Reads Grafana config file.
        """
        try:
            config = yaml.safe_load(read_file(self.CONFIG_GRAFANA_PATH))
            self.identity_store_id = config.get('Config', {}).get('IDENTITY_STORE_ID', '')
            valid_users = []
            for user in config.get('Config', {}).get('IDENTITY_CENTER_USERS', []):
                if len(user.keys()) == 3 and all(user.values()):
                    valid_users.append(
                        User(
                            username=user.get('USER_NAME'),
                            firstname=user.get('FIRST_NAME'),
                            lastname=user.get('LAST_NAME')
                        )
                    )
            self.identity_center_users = valid_users
            self.workspace_url = ''
        except yaml.YAMLError as e:
            terminate(f'Invalid structure of a grafana config file: {e}', ErrCode.EXCEPTION)

    @staticmethod
    def _update_config(path: Path, parent: str, param: str, val: str):
        """
        Updates parameter in the config file.

        :param path:    Path to the config file.
        :param parent:  Parent of the parameter it is grouped under.
        :param param:   Name of the parameter.
        :param val:     Value of the parameter.
        """
        new_lines = []
        val = val if val else 'null'

        with open(path, 'r') as config:
            text = config.read()
            config.seek(0)
            lines = config.readlines()

        exist = param in text
        for line in lines:
            if not exist and parent in line:
                # create new record
                new_lines.append(line)
                new_lines.append(f'    {param}: {val}\n')
            else:
                if param in line:
                    # update existing record
                    comment = '' if '#' not in line else '  #' + line.split('#')[-1].rstrip()
                    new_lines.append(f'    {param}: {val}{comment}\n')
                else:
                    # do not modify the line
                    new_lines.append(line)

        with open(path, 'w') as config:
            config.writelines(new_lines)
