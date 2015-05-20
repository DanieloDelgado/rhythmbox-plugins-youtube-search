# -*- Mode: python; coding: utf-8; tab-width: 4; indent-tabs-mode: nil; -*-
#
#    WikipediaSearch.py
#
#    Search for selected artist, album, track or genre at the click of a 
#    button.
#    Copyright (C) 2012-2013 Donagh Horgan <donagh.horgan@gmail.com>
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
from gi.repository import Gtk
from gi.repository import Gio

import webbrowser
import urllib.request, urllib.error, urllib.parse

class WikipediaSearchPlugin (GObject.Object, Peas.Activatable):
    object = GObject.property (type = GObject.Object)

    def __init__(self):
        GObject.Object.__init__(self)
        
    def log(self, function_name, message, error=False):
        if error:
            message_type = 'ERROR'
        else:
            message_type = 'DEBUG'
        print(function_name + ': ' + message_type + ': ' + message)

    def do_activate(self):
        self.log(self.do_activate.__name__, 'Activating plugin...')
        
        self.locations = [
            'browser-popup', 'playlist-popup',
            'podcast-episode-popup', 'queue-popup'
            ]
        search_types = ['Artist', 'Album', 'Track', 'Genre']
        search_actions = {
            'Artist': 'wikipedia-search-artist',
            'Album': 'wikipedia-search-album',
            'Track': 'wikipedia-search-track',
            'Genre': 'wikipedia-search-genre'
            }
        search_functions = {
            'Artist': self.search_artist,
            'Album': self.search_album,
            'Track': self.search_track,
            'Genre': self.search_genre
            }
        
        app = Gio.Application.get_default()
        
        section_item = Gio.MenuItem()
        section = Gio.Menu()
        for s in search_types:
            action = Gio.SimpleAction(name=search_actions[s])
            action.connect('activate', search_functions[s])
            app.add_action(action)
            
            section_item.set_label(s)
            section_item.set_detailed_action('app.' + search_actions[s])
            section.append_item(section_item)
        
        menu = Gio.Menu()
        menu.append_section(None, section)
        
        menu_item = Gio.MenuItem()
        menu_item.set_label('Search Wikipedia')
        menu_item.set_submenu(menu)
        for location in self.locations:
            app.add_plugin_menu_item(
                location, 'wikipedia-search', menu_item
                )
    
    def do_deactivate(self):
        self.log(self.do_deactivate.__name__, 'Deactivating plugin...')
        
        app = Gio.Application.get_default()
        for location in self.locations:
            app.remove_plugin_menu_item(location, 'wikipedia-search')

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
            metadata['genre'] = selected[0].get_string(RB.RhythmDBPropType.GENRE)
        return metadata

    def search_wikipedia(self, query):
        metadata = self.get_metadata()
        base_url = 'https://en.wikipedia.org/w/index.php?search='
        query_url = urllib.parse.quote(metadata[query])
        if query is 'genre':
            url = base_url + query_url + '+(music)'
        else:
            url = base_url + query_url
        
        self.log(self.search_wikipedia.__name__, 'Opening URL: ' + url)
        
        webbrowser.open(url)

    def search_artist(self, action, shell, *args):
        self.search_wikipedia('artist')

    def search_album(self, action, shell, *args):
        self.search_wikipedia('album')

    def search_track(self, action, shell, *args):
        self.search_wikipedia('track')

    def search_genre(self, action, shell, *args):
        self.search_wikipedia('genre')

