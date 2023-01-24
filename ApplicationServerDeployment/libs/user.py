# Copyright 2023 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

class User:
    """
    Describes identity center user.

    Attributes
    ----------
        username: str
            Username.
        firstname: str
            First name / given name.
        lastname: str
            Last name/ family name.
        id: str
            User id.
    """
    def __init__(self, username: str, firstname: str, lastname: str, id: str = ''):
        self.username = username
        self.firstname = firstname
        self.lastname = lastname
        self.id = id

    def __repr__(self):
        return f'User({self.username}, {self.firstname}, {self.lastname})'
