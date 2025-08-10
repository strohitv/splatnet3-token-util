import argparse

from data.app_config import AppConfig


class Echo:
	def __init__(self, command_name, app_config: AppConfig):
		self.command_name = command_name
		self.app_config = app_config

		self.parser = argparse.ArgumentParser(prog=self.command_name,
											  description='Prints a given text to the console',
											  conflict_handler='resolve')
		self.parser.add_argument('-h', '--help', required=False, help=argparse.SUPPRESS)
		self.parser.add_argument('TEXT', help='The text to be printed to console')

		self.description = self.parser.format_help()
		self.introduction = 'This command prints a given text to the console.'

	def execute(self, args):
		text = args.strip().replace(self.command_name, "", 1).strip()

		if text.startswith('\'') and text.endswith('\'') or text.startswith('"') and text.endswith('"'):
			text = text[1:-1]

		print(text)
