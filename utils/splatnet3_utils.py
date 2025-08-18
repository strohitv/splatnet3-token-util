import json
import os
import re
import sys
from urllib.parse import urljoin

import requests

import logging

from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


def create_headers(bullet_token, user_agent, web_view_version, na_country, na_language, app_language):
	graphql_head = {
		'Authorization': f'Bearer {bullet_token}',  # update every time it's called with current global var
		'Accept-Language': app_language,
		'User-Agent': user_agent,
		'X-Web-View-Ver': web_view_version,
		'Content-Type': 'application/json',
		'Accept': '*/*',
		'Origin': 'https://api.lp1.av5ja.srv.nintendo.net',
		'X-Requested-With': 'com.nintendo.znca',
		'Referer': f'https://api.lp1.av5ja.srv.nintendo.net?lang={app_language}&na_country={na_country}&na_lang={na_language}',
		'Accept-Encoding': 'gzip, deflate, br, zstd'
	}
	return graphql_head


def is_homepage_reachable(g_token, bullet_token, user_agent, web_view_version, na_country, na_language, app_language):
	logger.info(f'Trying to access SplatNet 3 homepage')

	headers = create_headers(bullet_token, user_agent, web_view_version, na_country, na_language, app_language)

	body = {"variables": {"naCountry": na_country},
			"extensions": {"persistedQuery": {"version": 1, "sha256Hash": "51fc56bbf006caf37728914aa8bc0e2c86a80cf195b4d4027d6822a3623098a8"}}}

	result = requests.post('https://api.lp1.av5ja.srv.nintendo.net/api/graphql', data=json.dumps(body), headers=headers, cookies={'_gtoken': g_token})

	if result.status_code < 300:
		logger.info(f'SplatNet 3 homepage could be reached, tokens are valid')
	else:
		logger.info(f'SplatNet 3 homepage returned status code {result.status_code}, tokens are invalid')

	logger.info('')

	return result.status_code < 300


def download_splatnet3_main_js(url):
	session = requests.Session()
	response = session.get(url)
	soup = BeautifulSoup(response.text, "html.parser")

	tag = 'script'
	inner = 'src'

	for res in soup.findAll(tag):
		if res.has_attr(inner):
			try:
				fileurl = urljoin(url, res.get(inner))

				if 'main.' in fileurl and '.js' in fileurl:
					filebin = session.get(fileurl)
					return filebin.text.encode(filebin.encoding)
			except Exception as exc:
				print(exc, file=sys.stderr)

	return None
