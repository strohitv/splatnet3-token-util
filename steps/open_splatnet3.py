import argparse
import io
import shlex
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
		self.parser.add_argument('--max-attempts', required=False, default=3,
								 help='How often the step should attempt to open SplatNet3 before giving up. Default: 3')
		self.parser.add_argument('--max-wait-secs', required=False, default=15,
								 help='How long the step should wait for SplatNet3 to load before it considers the attempt failed. Default: 15 seconds')
		self.parser.add_argument('-d', '--duration', required=False, default=500,
								 help='The frequency of how often this command should check whether SplatNet3 is open. Default: 500 ms')

		self.description = self.parser.format_help()
		self.introduction = 'This command causes the Nintendo Switch App to open and loads SplatNet3 afterwards.'

	def execute(self, args):
		only_args = shlex.split(args)[1:]
		parsed_args = self.parser.parse_args(only_args)

		found = False

		for i in range(int(parsed_args.max_attempts)):
			self.logger.info(f'Open SplatNet3 app - attempt {i + 1}/{parsed_args.max_attempts}')

			subprocess.run(f'{self.app_config.emulator_config.adb_path} shell am start https://s.nintendo.com/av5ja-lp1/znca/game/4834290508791808',
						   shell=True,
						   stdout=subprocess.PIPE,
						   stderr=subprocess.PIPE)

			start_time = time.time()

			while not found and time.time() - start_time < int(parsed_args.max_wait_secs):
				time.sleep(int(parsed_args.duration) / 1000.0)

				currently_opened_app_proc = subprocess.Popen(f'{self.app_config.emulator_config.adb_path} shell dumpsys activity recents',
															 shell=True,
															 stdout=subprocess.PIPE,
															 stderr=subprocess.PIPE)

				for line in io.TextIOWrapper(currently_opened_app_proc.stdout, encoding="utf-8"):
					if not line:
						break

					if self.app_config.debug:
						self.logger.info(line.strip())

					line = line.strip()

					if 'Recent #1' in line:
						break

					if 'GameWebActivity' in line:
						found = True
						self.logger.info(f'SplatNet3 found after {time.time() - start_time:.1f} seconds during attempt {i + 1}/{parsed_args.max_attempts}')
						break

			if found:
				break
			else:
				self.logger.info(f'Attempt {i + 1}/{parsed_args.max_attempts} failed.')

		if not found:
			raise Exception(f'Could not find SplatNet3 app after {parsed_args.max_attempts} attempts.')

		time.sleep(1)
