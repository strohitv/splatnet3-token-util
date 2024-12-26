from data.app_config import AppConfig


class Echo:
	def __init__(self, command_name, app_config: AppConfig):
		self.command_name = command_name
		self.app_config = app_config

	def execute(self, args):
		text = args.strip().replace(self.command_name, "", 1).strip()

		if text.startswith('\'') and text.endswith('\'') or text.startswith('"') and text.endswith('"'):
			text = text[1:-1]

		print(text)

	def description(self):
		return ('prints a given text to the command line.'
				f'\n#    - Use: "{self.command_name} [TEXT]" to print [TEXT]. If no text is given, it will print a new line.'
				f'\n#    - Example 1: "{self.command_name} hello, this is a test" to print "hello, this is a test"'
				f'\n#    - Example 2: "{self.command_name}" to print a new line')
