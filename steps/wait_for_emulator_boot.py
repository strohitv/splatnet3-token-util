import argparse
import io
import re
import shlex
import subprocess
import time

from data.app_config import AppConfig
from utils.step_doc_creator import get_arg_formatter

import logging


class WaitForEmulatorBoot:
	def __init__(self, command_name, app_config: AppConfig):
		self.logger = logging.getLogger(WaitForEmulatorBoot.__name__)

		self.command_name = command_name
		self.app_config = app_config

		self.parser = argparse.ArgumentParser(prog=self.command_name,
											  description='Waits until the emulator has been booted and is ready.',
											  formatter_class=get_arg_formatter(),
											  conflict_handler='resolve')
		self.parser.add_argument('-h', '--help', required=False, help=argparse.SUPPRESS)
		self.parser.add_argument('--max-wait-secs', required=False, default=60,
								 help='How long the step should wait for the emulator to boot before it considers the boot failed. Default: 60 seconds')
		self.parser.add_argument('-d', '--duration', required=False, default=500,
								 help='The frequency of how often this command should check whether SplatNet3 is open. Default: 500 ms')

		self.description = self.parser.format_help()
		self.introduction = 'This command causes the script to wait until the emulator is ready.'

	def execute(self, args):
		only_args = shlex.split(args)[1:]
		parsed_args = self.parser.parse_args(only_args)

		found = False

		self.logger.info(f'Waiting for emulator to complete the boot process...')

		start_time = time.time()

		while not found and time.time() - start_time < int(parsed_args.max_wait_secs):
			time.sleep(int(parsed_args.duration) / 1000.0)

			emulator_boot_check_proc = subprocess.Popen(f'{self.app_config.emulator_config.adb_path} shell dumpsys activity recents',
														shell=True,
														stdout=subprocess.PIPE,
														stderr=subprocess.PIPE)

			inactive_time = 0

			for line in io.TextIOWrapper(emulator_boot_check_proc.stdout, encoding="utf-8"):
				if not line:
					break

				if self.app_config.debug:
					self.logger.info(line.strip())

				line = line.strip()

				if 'lastActiveTime' in line:
					all_numbers = re.findall(r'\d+', line)
					if len(all_numbers) >= 2:
						if self.app_config.debug:
							self.logger.info(f'Found inactivity time after {time.time() - start_time:.1f} seconds')

						inactive_time = int(all_numbers[1])

				if 'Recent #1' in line and self.app_config.debug:
					self.logger.info(f'Found a second activity after {time.time() - start_time:.1f} seconds')

				if 'Recent #1' in line and inactive_time >= 1:
					found = True
					self.logger.info(f'Emulator boot finished after {time.time() - start_time:.1f} seconds')
					break

		if not found:
			raise Exception(f'Could not confirm a complete emulator boot after {parsed_args.max_wait_secs} seconds.')
