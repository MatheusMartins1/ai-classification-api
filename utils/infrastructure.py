"""
Developer: Matheus Martins da Silva
Creation Date: 11/2025
Contact Email: matheus.sql18@gmail.com
All rights reserved. This software is the property of Matheus Martins da Silva. No part of this software may be used, reproduced, distributed, or modified without the express written permission of the owner.
"""

import socket

import requests


def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception as e:
        return str(e)


def get_external_ip():
    try:
        external_ip = requests.get("https://api.ipify.org").text
        return external_ip
    except Exception as e:
        return str(e)
