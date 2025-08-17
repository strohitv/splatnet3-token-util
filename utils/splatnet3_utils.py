import json

import requests

import logging

logger = logging.getLogger(__name__)


def create_headers(bullet_token):
	lang = 'en-US'
	country = 'US'

	graphql_head = {
		'Authorization': f'Bearer {bullet_token}',  # update every time it's called with current global var
		'Accept-Language': lang,
		'User-Agent': 'Mozilla/5.0 (Linux; Android 11; Pixel 4) '
					  'AppleWebKit/537.36 (KHTML, like Gecko) '
					  'Chrome/120.0.6099.230 Mobile Safari',
		'X-Web-View-Ver': '6.0.0-9253fd84',
		'Content-Type': 'application/json',
		'Accept': '*/*',
		'Origin': 'https://api.lp1.av5ja.srv.nintendo.net',
		'X-Requested-With': 'com.nintendo.znca',
		'Referer': f'https://api.lp1.av5ja.srv.nintendo.net?lang={lang}&na_country={country}&na_lang={lang}',
		'Accept-Encoding': 'gzip, deflate, br, zstd'
	}
	return graphql_head


def is_homepage_reachable(g_token, bullet_token):
	logger.info(f'Trying to access SplatNet 3 homepage')

	headers = create_headers(bullet_token)

	body = {"variables": {"naCountry": "US"},
			"extensions": {"persistedQuery": {"version": 1, "sha256Hash": "51fc56bbf006caf37728914aa8bc0e2c86a80cf195b4d4027d6822a3623098a8"}}}

	result = requests.post('https://api.lp1.av5ja.srv.nintendo.net/api/graphql', data=json.dumps(body), headers=headers, cookies={'_gtoken': g_token})

	if result.status_code < 300:
		logger.info(f'SplatNet 3 homepage could be reached, tokens are valid')
	else:
		logger.info(f'SplatNet 3 homepage returned status code {result.status_code}, tokens are invalid')

	logger.info('')

	return result.status_code < 300
