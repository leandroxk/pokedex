import cherrypy
import os

from ntplib import NTPClient
from retrying import retry
from db.pokedex import Pokedex


class EmailAlert():

    def __init__(self):
        self.pokedex = Pokedex()

    @cherrypy.expose
    @cherrypy.tools.json_in()
    def index(self):
        print cherrypy.request.json
        encounter_data = cherrypy.request.json['message']
        pokemon_id = encounter_data.get('pokemon_id', 0)

        pokedex_data = self.pokedex.info(pokemon_id = pokemon_id)
        name = pokedex_data.get('ename', '')
        pokemon = Pokemon(pokemon_id, name)

        encounter = PokemonEncounter(pokemon, encounter_data)

        print 'id: %i' % pokemon.id
        print 'Name : %s' % pokemon.name
        print 'visible: %s' % encounter.is_valid()
        print 'remainig: %i' % encounter.remaining_secs()
        print 'loc: ' + encounter.get_map()


class Pokemon():

    def __init__(self, pokemon_id, name):
        self.id = pokemon_id
        self.name = name


class PokemonEncounter():

    def __init__(self, pokemon, encounter_data):
        self.pokemon = pokemon
        self.longitude = encounter_data.get('longitude', 0)
        self.time_until_hidden = encounter_data.get('time_until_hidden_ms', 0)
        self.latitude = encounter_data.get('latitude', 0)
        self.disappear_time = encounter_data.get('disappear_time', 0)

    def is_valid(self):
        return self._current_time() < self.disappear_time;

    def remaining_secs(self):
        remaining_s = self.disappear_time - self._current_time()
        if remaining_s > 0:
            return int(remaining_s)

        return 0;

    def get_map(self):
        return '%2.14f, %2.14f' % (self.latitude, self.longitude)

    @retry(stop_max_delay=10000)
    def _current_time(self):
        return NTPClient().request('gps.ntp.br').tx_time


config = {
    '/': {
        'tools.trailing_slash.on': False,
        'tools.gzip.on': True
    }
}

cherrypy.tree.mount(EmailAlert(), '/alert', config)
cherrypy.tree.mount(Pokedex(), '/pokedex', config)

cherrypy.config.update({
    'server.socket_host': '0.0.0.0',
    'server.socket_port': int(os.environ.get('PORT', 8080)),
})

cherrypy.engine.start()
cherrypy.engine.block()