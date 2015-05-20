#
#    YoutubeSearch.py
#
#    Search videos in Youtube for selected track, artist or album
#    Copyright (C) 2015 Daniel O. Delgado <danielo.delgado@gmail.com>
#
#    Based in the excellent plugin WikipediaSearch of Donagh Horgan
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

from gi.repository import GObject
from gi.repository import Peas
from gi.repository import RB
from gi.repository import Gio
import webbrowser
import urllib.parse, urllib.request
import re

class YoutubeSearch (GObject.Object, Peas.Activatable):
	object = GObject.property(type=GObject.Object)
	def __init__(self):
		GObject.Object.__init__(self)

	def do_activate(self):

		self.locations = [
			'browser-popup', 'playlist-popup', 'queue-popup'
			]
		search_types = ['Track','Artist','Album']
		search_actions = {
			'Track' : 'youtube-search-track',
			'Artist' : 'youtube-search-artist',
			'Album' : 'youtube-search-album',
			}
		search_functions = {
			'Track' : self.search_track,
			'Artist' : self.search_artist,
			'Album' : self.search_album,
			}

		app = Gio.Application.get_default()
		section_item = Gio.MenuItem()
		section = Gio.Menu()
		for key in search_types:
			action = Gio.SimpleAction(name = search_actions[key])
			action.connect('activate', search_functions[key])
			app.add_action(action)
			section_item.set_label(key)
			section_item.set_detailed_action('app.' + search_actions[key])
			section.append_item(section_item)

		menu = Gio.Menu()
		menu.append_section(None, section)

		menu_item = Gio.MenuItem()
		menu_item.set_label('Youtube Search')
		menu_item.set_submenu(menu)
		for location in self.locations:
			app.add_plugin_menu_item( location, 'youtube-search', menu_item )

	def do_deactivate(self):
		app = Gio.Application.get_default()
		for location in self.locations:
			app.remove_plugin_menu_item(location, 'youtube-search')

	def get_metadata(self):
		shell = self.object
		page = shell.props.selected_page
		if not hasattr(page, 'get_entry_view'):
			return
		selected = page.get_entry_view().get_selected_entries()
		metadata = {}
		if selected != []:
			metadata['artist'] = selected[0].get_string(RB.RhythmDBPropType.ARTIST)
			metadata['album'] = selected[0].get_string(RB.RhythmDBPropType.ALBUM)
			metadata['track'] = selected[0].get_string(RB.RhythmDBPropType.TITLE)
		return metadata

	def search_youtube(self, query):
		shell = self.object
		metadata = self.get_metadata()
		base_url = 'https://www.youtube.com/results?search_query='
		query_url = urllib.parse.quote(metadata[query])

		if query in ['album','track']:
			query_url = urllib.parse.quote(metadata['artist']+' '+metadata[query])
			url = base_url + query_url
			print(url)
			page = urllib.request.urlopen(url).read()
			url = 'https://www.youtube.com'+re.search('\/watch\?v=[\-a-zA-Z0-9]*',page.decode()).group(0)
			shell.props.shell_player.pause()
		else:
			query_url = urllib.parse.quote(metadata[query])
			url = base_url + query_url
		webbrowser.open(url)

	def search_track(self, action, shell, *args):
		self.search_youtube('track')

	def search_artist(self, action, shell, *args):
		self.search_youtube('artist')

	def search_album(self, action, shell, *args):
		self.search_youtube('album')
