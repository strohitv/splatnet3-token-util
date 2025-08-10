import argparse


def create_step_doc(steps, file='./steps_documentation.md'):
	readme = '(Note: this file gets generated from `./utils/step_doc_creator.py`, do not manually change it)\n\n# Steps Documentation\nThis document lists and describes all possible steps you can use in the `boot.txt` and `cleanup.txt` files. These files use some kind of "custom bash script format" which is very simple and contains all the steps required to control the emulator one step after another. There are no variables, no loops, no ifs and other structures bash usually provides, only a few allowed commands.\n\nHere is the documentation of all commands ("steps") you can use to control the emulator.'

	for key in steps:
		step = steps[key]
		readme += f'\n\n## {step.command_name}\n{step.introduction}\n\n### Usage:\n```\n{step.description}\n```'

	with open(file, 'w') as f:
		f.write(readme)


def get_arg_formatter():
	return lambda prog: argparse.HelpFormatter(prog, indent_increment=2, max_help_position=50, width=110)
