import argparse
import subprocess
import time

from data.app_config import AppConfig
from utils.step_doc_creator import get_arg_formatter

import logging


class OpenSplatNet3:
	def __init__(self, command_name, app_config: AppConfig):
		self.logger = logging.getLogger(OpenSplatNet3.__name__)

		self.command_name = command_name
		self.app_config = app_config

		self.parser = argparse.ArgumentParser(prog=self.command_name,
											  description='Opens the SplatNet3 app inside the Nintendo Switch App immediately.',
											  formatter_class=get_arg_formatter(),
											  conflict_handler='resolve')
		self.parser.add_argument('-h', '--help', required=False, help=argparse.SUPPRESS)

		self.description = self.parser.format_help()
		self.introduction = 'This command causes the Nintendo Switch App to open and loads SplatNet3 afterwards.'

	def execute(self, args):
		self.logger.info(f'Open SplatNet3 app.')
		subprocess.run(f'{self.app_config.emulator_config.adb_path} shell am start https://s.nintendo.com/av5ja-lp1/znca/game/4834290508791808',
					   shell=True,
					   stdout=subprocess.PIPE,
					   stderr=subprocess.PIPE)
		time.sleep(1)
