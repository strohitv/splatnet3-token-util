import argparse
import subprocess
import time

from data.app_config import AppConfig
from utils.step_doc_creator import get_arg_formatter

import logging


class ShutdownEmulator:
	def __init__(self, command_name, app_config: AppConfig):
		self.logger = logging.getLogger(ShutdownEmulator.__name__)

		self.command_name = command_name
		self.app_config = app_config

		self.parser = argparse.ArgumentParser(prog=self.command_name,
											  description='Triggers an emulator shutdown..',
											  formatter_class=get_arg_formatter(),
											  conflict_handler='resolve')
		self.parser.add_argument('-h', '--help', required=False, help=argparse.SUPPRESS)

		self.description = self.parser.format_help()
		self.introduction = 'This command causes the Emulator to shut down.'

	def execute(self, args):
		self.logger.info(f'Shutting down.')
		subprocess.run(f'{self.app_config.emulator_config.adb_path} shell reboot -p',
					   shell=True,
					   stdout=subprocess.PIPE,
					   stderr=subprocess.PIPE)
		time.sleep(1)
