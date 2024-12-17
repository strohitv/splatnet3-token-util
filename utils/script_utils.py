

def execute_script(all_available_steps, script_location, script_name, is_debug):
	print(f'Executing {script_name} script...')
	with open(script_location, 'r') as boot_script:
		while True:
			line = boot_script.readline()

			if not line:
				break

			line = line.strip()

			if is_debug:
				print(line)

			if line.startswith('#') or line == '':
				continue

			command = line.split(' ')[0]
			if command in all_available_steps:
				step = all_available_steps[command]
				step.execute(line)
	print(f'Finished {script_name} script execution.')
	print()
