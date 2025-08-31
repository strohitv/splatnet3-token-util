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
		self.parser.add_argument('--max-wait-secs', required=False, default=45,
								 help='How long the step should wait for SplatNet3 to load before it considers the attempt failed. Default: 45 seconds')
		self.parser.add_argument('-d', '--duration', required=False, default=500,
								 help='The frequency of how often this command should check whether SplatNet3 is open. Default: 500 ms')

		self.description = self.parser.format_help()
		self.introduction = 'This command attempts to open the Nintendo Switch App and load SplatNet3 afterwards.'

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

				currently_opened_app_proc = subprocess.Popen(f'{self.app_config.emulator_config.adb_path} shell dumpsys activity processes',
															 shell=True,
															 stdout=subprocess.PIPE,
															 stderr=subprocess.PIPE)

				is_splatnet_app = False
				game_web_activity_loaded = False
				active_connections = 0

				for line in io.TextIOWrapper(currently_opened_app_proc.stdout, encoding="utf-8"):
					if not line:
						break

					if self.app_config.debug:
						self.logger.info(line.strip())

					line = line.strip()

					if '*APP*' in line and not is_splatnet_app and active_connections > 0:
						found = active_connections <= 3 and game_web_activity_loaded
						break

					if 'com.nintendo.znca/.ui.gameweb.GameWebActivity' in line:
						game_web_activity_loaded = True
						continue

					if '*APP*' in line and not is_splatnet_app and 'com.nintendo.znca' in line:
						is_splatnet_app = True
						found = True
						continue

					if '*APP*' in line and is_splatnet_app and not 'com.nintendo.znca' in line:
						is_splatnet_app = False
						continue

					if '- ConnectionRecord{' in line and is_splatnet_app:
						active_connections += 1
						continue

			if not found:
				self.logger.info(f'Opening SplatNet3 - attempt {i + 1}/{parsed_args.max_attempts} failed.')
			else:
				self.logger.info(f'Opening SplatNet3 - attempt {i + 1}/{parsed_args.max_attempts} success - done after {time.time() - start_time:.1f} seconds.')
				break

		if not found:
			raise Exception(f'Could not open SplatNet3 app in {parsed_args.max_attempts} attempts.')
