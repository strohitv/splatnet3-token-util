import argparse
import subprocess
import shlex

from data.app_config import AppConfig
from utils.step_doc_creator import get_arg_formatter


class Tap:
	def __init__(self, command_name, app_config: AppConfig):
		self.command_name = command_name
		self.app_config = app_config

		self.parser = argparse.ArgumentParser(prog=self.command_name,
											  description='Taps a given position (X, Y) on the screen once',
											  formatter_class=get_arg_formatter(),
											  conflict_handler='resolve')
		self.parser.add_argument('-h', '--help', required=False, help=argparse.SUPPRESS)
		self.parser.add_argument('-x', '--x', required=True, help='The X coordinate of the position which should be tapped')
		self.parser.add_argument('-y', '--y', required=True, help='The Y coordinate of the position which should be tapped')

		self.description = self.parser.format_help()
		self.introduction = 'This command will tap a given position on the screen.'

	def execute(self, args):
		only_args = shlex.split(args)[1:]
		parsed_args = self.parser.parse_args(only_args)

		print(f'Tapping position ({parsed_args.x}, {parsed_args.y}).')
		subprocess.run(f'{self.app_config.emulator_config.adb_path} shell input tap {parsed_args.x} {parsed_args.y}',
					   shell=True,
					   stdout=subprocess.PIPE,
					   stderr=subprocess.PIPE)
