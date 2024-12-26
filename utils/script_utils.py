from io import StringIO


def execute(line, all_available_steps):
	# split line into different statements
	commands = ['']

	current_str_char = None
	for i in range(len(line)):
		if line[i] == '"' or line[i] == '\'':
			if current_str_char is None:
				current_str_char = line[i]
			elif line[i] == current_str_char:
				current_str_char = None

		if line[i] == ';' and current_str_char is None:
			commands.append('')
		elif line[i] == '#' and current_str_char is None:
			# found comment, ignore from here on
			break
		else:
			commands[-1] += line[i]

	if current_str_char is not None:
		# last command is broken, remove
		commands[-1] = '# ' + commands[-1]

	# execute statements
	for cmd in commands:
		command = cmd.strip()

		if command.startswith('#') or command == '':
			continue

		step = command.split(' ')[0]
		if step in all_available_steps:
			found_step = all_available_steps[step]
			found_step.execute(command)


def analyse_line_break_elligibility(line):
	is_eligible = True

	current_str_char = None
	for i in range(len(line)):
		if line[i] == '"' or line[i] == '\'':
			if current_str_char is None:
				current_str_char = line[i]
			elif line[i] == current_str_char:
				current_str_char = None

		if line[i] == '#' and current_str_char is None:
			# found comment, ignore from here on
			is_eligible = False
			break

	return is_eligible, current_str_char is not None


def execute_script(all_available_steps, script_location, script_name, is_debug):
	print(f'Executing {script_name} script...')
	with open(script_location, 'r') as boot_script:
		while True:
			line = boot_script.readline()

			if not line:
				break

			is_eligible_for_line_break, string_open = analyse_line_break_elligibility(line)

			while string_open or (is_eligible_for_line_break and line.strip().endswith('\\')):
				next_line = boot_script.readline()
				if next_line:
					line = line.strip()

					if line[-1] == '\\':
						line = line[:-1]

					line = '{0} {1}'.format(line.strip(), next_line.strip())
					is_eligible_for_line_break, string_open = analyse_line_break_elligibility(line)
				else:
					break

			line = line.strip()

			if is_debug:
				print(line)

			execute(line, all_available_steps)
	print(f'Finished {script_name} script execution.')
	print()
