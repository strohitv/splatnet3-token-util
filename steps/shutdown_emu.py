import argparse
import io
import shlex
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
											  description='Triggers an emulator shutdown.',
											  formatter_class=get_arg_formatter(),
											  conflict_handler='resolve')
		self.parser.add_argument('-h', '--help', required=False, help=argparse.SUPPRESS)
		self.parser.add_argument('--max-attempts', required=False, default=3,
								 help='How often the step should attempt to shut the emulator down before giving up. Default: 3')
		self.parser.add_argument('--max-wait-secs', required=False, default=30,
								 help='How long the step should wait for the emulator to shutdown before it considers the attempt failed. Default: 30 seconds')
		self.parser.add_argument('-d', '--duration', required=False, default=500,
								 help='The frequency of how often this command should check whether the emulator is still running. Default: 500 ms')

		self.description = self.parser.format_help()
		self.introduction = 'This command causes the Emulator to shut down.'

	def execute(self, args):

		only_args = shlex.split(args)[1:]
		parsed_args = self.parser.parse_args(only_args)

		stopped = False

		for i in range(int(parsed_args.max_attempts)):
			self.logger.info(f'Shutting down emulator - attempt {i + 1}/{parsed_args.max_attempts}')

			subprocess.run(f'{self.app_config.emulator_config.adb_path} shell reboot -p',
						   shell=True,
						   stdout=subprocess.PIPE,
						   stderr=subprocess.PIPE)

			stopped = False
			start_time = time.time()

			while not stopped and time.time() - start_time < int(parsed_args.max_wait_secs):
				time.sleep(int(parsed_args.duration) / 1000.0)

				currently_opened_app_proc = subprocess.Popen(f'{self.app_config.emulator_config.adb_path} devices',
															 shell=True,
															 stdout=subprocess.PIPE,
															 stderr=subprocess.PIPE)

				stopped = True

				for line in io.TextIOWrapper(currently_opened_app_proc.stdout, encoding="utf-8"):
					if not line:
						break

					if self.app_config.debug:
						self.logger.info(line.strip())

					line = line.strip()

					if not 'List of devices attached' in line and len(line) > 0:
						stopped = False
						break

			if not stopped:
				self.logger.info(f'Shutting down emulator - attempt {i + 1}/{parsed_args.max_attempts} failed.')
			else:
				self.logger.info(f'Shutting down emulator - attempt {i + 1}/{parsed_args.max_attempts} success - done after {time.time() - start_time:.1f} seconds.')
				break

		if not stopped:
			raise Exception(f'Could not shut down emulator after {parsed_args.max_attempts} attempts.')

	# time.sleep(1)
