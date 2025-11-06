"""
Developer: Matheus Martins da Silva
Creation Date: 11/2024
Contact Email: matheus.sql18@gmail.com
All rights reserved. This software is the property of Matheus Martins da Silva. No part of this software may be used, reproduced, distributed, or modified without the express written permission of the owner.
"""

import datetime
import psutil
import datetime
import sys
import os
from pytz import timezone
import warnings

from utils.LoggerConfig import LoggerConfig

warnings.simplefilter(action="ignore", category=FutureWarning)

today = datetime.datetime.now(tz=timezone("America/Sao_Paulo"))


class CameraLogManager:
    def __init__(self, _camera):
        self._camera = _camera

        self.logs = []
        # TODO: Change logger to fill self.logs
        self.logger = LoggerConfig.add_file_logger(
            name="camera", filename=None, dir_name=None, prefix="camera"
        )

    def get_logs(self):
        """
        Get the action logs.

        Returns:
            A list of action logs.
        """
        return self.logs
