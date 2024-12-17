import base64
import os


def read_in_chunks(file_object, chunk_size=10 * 1024 * 1024):
	while True:
		data = file_object.read(chunk_size)
		if not data:
			break
		yield data


def search_for_tokens(app_config):
	snapshot_path = os.path.expanduser(os.path.join(app_config.snapshot_dir, app_config.snapshot_name, 'ram.bin'))

	gtoken = None
	bullet_token = None
	session_token = None

	# analyse snapshot and find values
	print(f'Searching for tokens...')
	with open(snapshot_path, 'rb') as f:
		for piece in read_in_chunks(f):
			# _gtoken search
			if gtoken is None and b'_gtoken=ey' in piece:
				gtoken = ''
				index = piece.index(b'_gtoken=ey') + len(b'_gtoken=')
				while index < len(piece):
					next_piece = piece[index]
					if chr(next_piece) == '\x00':
						break
					gtoken += chr(next_piece)
					index += 1

				if len(gtoken) < 850:
					# TODO jwt validation
					gtoken = None

			# bullet_token search
			if bullet_token is None and b'"bulletToken":"' in piece:
				bullet_token = ''
				index = piece.index(b'"bulletToken":"') + len(b'"bulletToken":"')
				while index < len(piece):
					next_piece = piece[index]
					if chr(next_piece) == '\x00':
						bullet_token = None
						break
					if chr(next_piece) == '"':
						break
					bullet_token += chr(next_piece)
					index += 1

				if len(bullet_token) > 100:
					try:
						base64.b64decode(bullet_token)
					except Exception as e:
						bullet_token = None
				else:
					bullet_token = None

			# session_token search
			if session_token is None and b'eyJhbGciOiJIUzI1NiJ9' in piece:
				session_token = ''
				index = piece.index(b'eyJhbGciOiJIUzI1NiJ9')
				while index < len(piece):
					next_piece = piece[index]
					if chr(next_piece) == '\x00':
						break
					session_token += chr(next_piece)
					index += 1

				if len(session_token) < 260:
					# TODO jwt validation
					session_token = None

			if app_config.debug:
				print('next chunk done')

	print('Result:')
	print('- SUCCESS\tgToken' if gtoken is not None else '- FAIL\t\tgToken')
	print('- SUCCESS\tbulletToken' if bullet_token is not None else '- FAIL\t\tbulletToken')
	print('- SUCCESS\tsessionToken' if session_token is not None else '- FAIL\t\tsessionToken')
	print()

	return gtoken, bullet_token, session_token
