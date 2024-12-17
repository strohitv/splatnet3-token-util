import argparse
import subprocess
import shlex

from data.config import Config


class Tap:
	def __init__(self, command_name, config: Config):
		self.command_name = command_name
		self.config = config

	def execute(self, args):
		only_args = shlex.split(args)[1:]

		parser = argparse.ArgumentParser()
		parser.add_argument('-x', '--x', required=False, default=5)
		parser.add_argument('-y', '--y', required=False, default=5)
		parsed_args = parser.parse_args(only_args)

		print(f'Tapping position ({parsed_args.x}, {parsed_args.y}).')
		subprocess.run(f'{self.config.adb_path} shell input tap {parsed_args.x} {parsed_args.y}', shell=True)

	def description(self):
		return ('taps a given position on the screen.'
				f'\n#    - Use: "{self.command_name} [X] [Y]" to tap the position (X, Y) on the screen.'
				f'\n#    - Example 1: "{self.command_name} -x 100 -y 200" to tap the position (100, 200) on the screen.'
				f'\n#    - Example 2: "{self.command_name} --x 100 --y 200" to tap the position (100, 200) on the screen.')
