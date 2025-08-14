import argparse
import subprocess
import shlex

from data.app_config import AppConfig
from utils.step_doc_creator import get_arg_formatter


class Type:
	def __init__(self, command_name, app_config: AppConfig):
		self.command_name = command_name
		self.app_config = app_config

		self.parser = argparse.ArgumentParser(prog=self.command_name,
											  description='Types a given text on the android keyboard',
											  formatter_class=get_arg_formatter(),
											  conflict_handler='resolve')
		self.parser.add_argument('-h', '--help', required=False, help=argparse.SUPPRESS)
		self.parser.add_argument('-t', '--text', required=True, help='The text to type')

		self.description = self.parser.format_help()
		self.introduction = 'This command will type a given text on the android keyboard.'

	def execute(self, args):
		only_args = shlex.split(args)[1:]
		parsed_args = self.parser.parse_args(only_args)

		print(f'Typing text "{parsed_args.text}".')
		subprocess.run(f'{self.app_config.emulator_config.adb_path} shell input text "{parsed_args.text.replace(" ", "%s")}"',
					   shell=True,
					   stdout=subprocess.PIPE,
					   stderr=subprocess.PIPE)
