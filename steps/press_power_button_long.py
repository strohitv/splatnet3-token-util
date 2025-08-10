import argparse
import subprocess
import time

from data.app_config import AppConfig


class PressPowerButtonLong:
	def __init__(self, command_name, app_config: AppConfig):
		self.command_name = command_name
		self.app_config = app_config

		self.parser = argparse.ArgumentParser(prog=self.command_name,
											  description='Presses the power button for a long time',
											  conflict_handler='resolve')
		self.parser.add_argument('-h', '--help', required=False, help=argparse.SUPPRESS)

		self.description = self.parser.format_help()
		self.introduction = 'This command presses the power button for a long time, which usually opens the power menu.'

	def execute(self, args):
		print(f'Pressing the power button for a long time.')
		subprocess.run(f'{self.app_config.emulator_config.adb_path} shell input keyevent --longpress KEYCODE_POWER',
					   shell=True,
					   stdout=subprocess.PIPE,
					   stderr=subprocess.PIPE)
		time.sleep(1)
