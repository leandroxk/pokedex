import cherrypy
import os

class EmailAlert():

    @cherrypy.expose
    @cherrypy.tools.json_in()
    def index(self):
    	print Message(cherrypy.request.json).pokemon_id

        return "Hello World!"


class Message():

	def __init__(self, json):
		body = json['message']
		self.pokemon_id = body['pokemon_id']
		self.longitude = body['longitude']
		self.time_until_hidden = body['time_until_hidden_ms']
		self.latitude = body['latitude']


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
