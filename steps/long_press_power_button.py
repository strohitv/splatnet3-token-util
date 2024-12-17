import subprocess
import time

from data.app_config import AppConfig


class LongPressPowerButton:
	def __init__(self, command_name, app_config: AppConfig):
		self.command_name = command_name
		self.app_config = app_config

	def execute(self, args):
		print(f'Pressing the power button for a long time.')
		subprocess.run(f'{self.app_config.adb_path} shell input keyevent --longpress KEYCODE_POWER',
					   shell=True,
					   stdout=subprocess.PIPE,
					   stderr=subprocess.PIPE)
		time.sleep(1)

	def description(self):
		return ('presses the power button for a long time.'
				f'\n#    - Use: "{self.command_name}" to press the power button for a long time.')
