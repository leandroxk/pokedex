import cherrypy
import os

from ntplib import NTPClient
from retrying import retry


class EmailAlert():

    @cherrypy.expose
    @cherrypy.tools.json_in()
    def index(self):
    	pokemon = Pokemon(cherrypy.request.json)
    	print pokemon.id
    	print pokemon.is_visible()
    	print pokemon.remaining_secs()


class Pokemon():

	def __init__(self, json):
		body = json['message']
		self.id = body['pokemon_id']
		self.longitude = body['longitude']
		self.time_until_hidden = body['time_until_hidden_ms']
		self.latitude = body['latitude']
		self.disappear_time = body['disappear_time']

	def is_visible(self):
		return self._current_time() < self.disappear_time;

	def remaining_secs(self):
		remaining_s = self.disappear_time - self._current_time()
		if remaining_s > 0:
			return int(remaining_s)

		return 0;

	def get_map(self):
		return ""

	@retry(stop_max_delay=10000)
	def _current_time(self):
		return NTPClient().request('gps.ntp.br').tx_time


config = {
    'global': {
        'server.socket_host': '0.0.0.0',
        'server.socket_port': int(os.environ.get('PORT', 8080)),
    },
	'/': {
        'tools.trailing_slash.on': False,
        'tools.gzip.on': True
    }
}

cherrypy.quickstart(EmailAlert(), '/alert', config)
