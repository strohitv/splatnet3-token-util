import argparse
import shlex
import subprocess

from data.app_config import AppConfig
from utils.step_doc_creator import get_arg_formatter


class Swipe:
	def __init__(self, command_name, app_config: AppConfig):
		self.command_name = command_name
		self.app_config = app_config

		self.parser = argparse.ArgumentParser(prog=self.command_name,
											  description='Swipes from a given starting point (X1, Y1) to a given target point (X2, Y2) on the screen over the span of a given duration',
											  formatter_class=get_arg_formatter(),
											  conflict_handler='resolve')
		self.parser.add_argument('-h', '--help', required=False, help=argparse.SUPPRESS)
		self.parser.add_argument('-x1', '--x1', required=True, help='The X coordinate of the starting position of the swipe')
		self.parser.add_argument('-y1', '--y1', required=True, help='The Y coordinate of the starting position of the swipe')
		self.parser.add_argument('-x2', '--x2', required=True, help='The X coordinate of the target position of the swipe')
		self.parser.add_argument('-y2', '--y2', required=True, help='The Y coordinate of the target position of the swipe')
		self.parser.add_argument('-d', '--duration', required=False, default=500, help='The duration how long the swipe should take. Default: 500 ms')

		self.description = self.parser.format_help()
		self.introduction = 'This command will swipe from one position to another over the span of a given duration.'

	def execute(self, args):
		only_args = shlex.split(args)[1:]
		parsed_args = self.parser.parse_args(only_args)

		print(f'Swiping from position ({parsed_args.x1}, {parsed_args.y1}) to ({parsed_args.x2}, {parsed_args.y2}) in {parsed_args.duration} milliseconds.')
		subprocess.run(
			f'{self.app_config.emulator_config.adb_path} shell input swipe {parsed_args.x1} {parsed_args.y1} {parsed_args.x2} {parsed_args.y2} {parsed_args.duration}',
			shell=True,
			stdout=subprocess.PIPE,
			stderr=subprocess.PIPE)
