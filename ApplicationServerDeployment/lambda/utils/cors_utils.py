# Copyright 2023 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

"""
Utility functions for cors handling.
"""

import os


def get_gui_bucket_url_for_cors():
    url = os.environ.get("GUI_BUCKET_URL")
    if url[-1] == '/':
        url = url[:-1]  # cors needs last slash to be stripped
    return url
