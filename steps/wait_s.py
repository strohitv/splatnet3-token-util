import argparse
import shlex
import time

from data.app_config import AppConfig
from utils.step_doc_creator import get_arg_formatter


class WaitS:
	def __init__(self, command_name, app_config: AppConfig):
		self.command_name = command_name
		self.app_config = app_config

		self.parser = argparse.ArgumentParser(prog=self.command_name,
											  description='Waits for the given amount of seconds',
											  formatter_class=get_arg_formatter(),
											  conflict_handler='resolve')
		self.parser.add_argument('-h', '--help', required=False, help=argparse.SUPPRESS)
		self.parser.add_argument('seconds', default=5, help='The amount of seconds to wait')

		self.description = self.parser.format_help()
		self.introduction = 'This command will block the execution of the script for the given amount of seconds.'

	def execute(self, args):
		only_args = shlex.split(args)[1:]
		parsed_args = self.parser.parse_args(only_args)

		print(f'Waiting for {parsed_args.seconds} seconds.')
		time.sleep(float(parsed_args.seconds))
