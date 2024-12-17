import subprocess
import time

from data.config import Config


class LongPressPowerButton:
	def __init__(self, command_name, config: Config):
		self.command_name = command_name
		self.config = config

	def execute(self, args):
		print(f'Pressing the power button for a long time.')
		subprocess.run(f'{self.config.adb_path} shell input keyevent --longpress KEYCODE_POWER', shell=True)
		time.sleep(1)

	def description(self):
		return ('presses the power button for a long time.'
				f'\n#    - Use: "{self.command_name}" to press the power button for a long time.')
