import argparse
import shlex
import subprocess

from data.config import Config


class Swipe:
	def __init__(self, command_name, config: Config):
		self.command_name = command_name
		self.config = config

	def execute(self, args):
		only_args = shlex.split(args)[1:]

		parser = argparse.ArgumentParser()
		parser.add_argument('-x1', '--x1', required=True)
		parser.add_argument('-y1', '--y1', required=True)
		parser.add_argument('-x2', '--x2', required=True)
		parser.add_argument('-y2', '--y2', required=True)
		parser.add_argument('-d', '--duration', required=False)
		parsed_args = parser.parse_args(only_args)

		print(f'Swiping from position ({parsed_args.x1}, {parsed_args.y1}) to ({parsed_args.x2}, {parsed_args.y2}) in {parsed_args.duration} milliseconds.')
		subprocess.run(f'{self.config.adb_path} shell input swipe {parsed_args.x1} {parsed_args.y1} {parsed_args.x2} {parsed_args.y2} {parsed_args.duration}',
						   shell=True,
						   stdout=subprocess.PIPE,
						   stderr=subprocess.PIPE)

	def description(self):
		return ('swipes from a given position to another given position on the screen.'
				f'\n#    - Use: "{self.command_name} [X1] [Y1] [X2] [Y2] [DURATION_MS]" to swipe from position (X1, Y1) to (X2, Y2) on the screen for [DURATION_MS] milliseconds.'
				f'\n#          If no duration is given, the swipe will last for 500 ms.'
				f'\n#    - Example 1: "{self.command_name} -x1 100 -y1 200 -x2 300 -y2 400 -d 500" to swipe from position (100, 200) to (300, 400) on the screen for 500 ms.'
				f'\n#    - Example 2: "{self.command_name} --x1 100 --y1 200 --x2 300 --y2 400 --duration 500" to swipe from position (100, 200) to (300, 400) on the screen for 500 ms.')
