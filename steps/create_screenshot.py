import argparse
import os
import shlex
import subprocess
import time

from data.app_config import AppConfig
from utils.step_doc_creator import get_arg_formatter

import logging


class CreateScreenshot:
	def __init__(self, command_name, app_config: AppConfig):
		self.logger = logging.getLogger(CreateScreenshot.__name__)

		self.command_name = command_name
		self.app_config = app_config

		self.parser = argparse.ArgumentParser(prog=self.command_name,
											  description='Creates a screenshot of the Emulator',
											  formatter_class=get_arg_formatter(),
											  conflict_handler='resolve')
		self.parser.add_argument('-h', '--help', required=False, help=argparse.SUPPRESS)
		self.parser.add_argument('-p', '-path', '--path', required=False, default='./screenshots/screenshot.png',
								 help='The file path where the screenshot of the emulator should be stored. Default: "./screenshots/screenshot.png"')

		self.description = self.parser.format_help()
		self.introduction = 'This command creates a screenshot of the Emulator and saves it to the given location.'

	def execute(self, args):
		only_args = shlex.split(args)[1:]
		parsed_args = self.parser.parse_args(only_args)

		self.logger.info(f'Saving a screenshot of the emulator at {parsed_args.path}...')
		os.makedirs(os.path.dirname(parsed_args.path), exist_ok=True)

		while not os.path.exists(parsed_args.path):
			subprocess.run(f'{self.app_config.emulator_config.adb_path} exec-out screencap -p > {parsed_args.path}',
						   shell=True,
						   stdout=subprocess.PIPE,
						   stderr=subprocess.PIPE)
			time.sleep(1)

		self.logger.info(f'Screenshot saved to {parsed_args.path}.')
