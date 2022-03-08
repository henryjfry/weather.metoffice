# -*- coding: utf-8 -*-

# *  This Program is free software; you can redistribute it and/or modify
# *  it under the terms of the GNU General Public License as published by
# *  the Free Software Foundation; either version 2, or (at your option)
# *  any later version.
# *
# *  This Program is distributed in the hope that it will be useful,
# *  but WITHOUT ANY WARRANTY; without even the implied warranty of
# *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# *  GNU General Public License for more details.
# *
# *  You should have received a copy of the GNU General Public License
# *  along with XBMC; see the file COPYING. If not, write to
# *  the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
# *  http://www.gnu.org/copyleft/gpl.html

import xbmc
import xbmcgui
import sys
import time
import json

weather_time = xbmcgui.Window(10000).getProperty("weather_time")

window_id = xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"GUI.GetProperties","params":{"properties":["currentwindow", "currentcontrol"]},"id":1}')
window_id = json.loads(window_id)

if 'Weather' in str(window_id):
	weather_time = 'True'

if weather_time != 'True':
	exit()

if xbmc.getCondVisibility("System.ScreenSaverActive"):
	xbmc.executeJSONRPC('{"jsonrpc": "2.0", "id": 1, "method": "Input.Select"}')

import socket
socket.setdefaulttimeout(20)
try:
    import utilities, properties, urlcache
    from utilities import gettext as _
    from constants import WINDOW, ADDON, API_KEY, CURRENT_VIEW, ADDON_DATA_PATH, ADDON_BANNER_PATH
except:
    try:
        import sys
        import os,sys,inspect
        currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
        parentdir = os.path.dirname(currentdir) + '/weather.metoffice/src'
        sys.path.insert(0,parentdir) 
        # insert at 1, 0 is the script path (or '' in REPL)
        import pytz
        from metoffice import default
        from metoffice import utilities, properties, urlcache
        from metoffice.utilities import gettext as _
        from metoffice.constants import WINDOW, ADDON, API_KEY, CURRENT_VIEW, ADDON_DATA_PATH, ADDON_BANNER_PATH
    except:
        from metoffice import default
        from metoffice import utilities, properties, urlcache
        from metoffice.utilities import gettext as _
        from metoffice.constants import WINDOW, ADDON, API_KEY, CURRENT_VIEW, ADDON_DATA_PATH, ADDON_BANNER_PATH
    #from metoffice import default
    #from metoffice import utilities, properties, urlcache, astronomy, constants, properties, routing, setlocation, urlcache




@utilities.failgracefully
def main():
    if ADDON.getSetting('EraseCache') == 'true':
        try:
            urlcache.URLCache(ADDON_DATA_PATH).erase()
        finally:
            ADDON.setSetting('EraseCache', 'false')#@UndefinedVariable

    if not API_KEY:
        raise Exception(_("No API Key."), _("Enter your Met Office API Key under settings."))

    properties.observation()
    properties.daily()
    properties.threehourly()
    properties.sunrisesunset()

    WINDOW.setProperty('WeatherProvider', ADDON.getAddonInfo('name'))#@UndefinedVariable
    WINDOW.setProperty('WeatherProviderLogo', ADDON_BANNER_PATH)#@UndefinedVariable
    WINDOW.setProperty('ObservationLocation', ADDON.getSetting('ObservationLocation'))#@UndefinedVariable
    WINDOW.setProperty('Current.Location', ADDON.getSetting('ForecastLocation'))#@UndefinedVariable
    WINDOW.setProperty('ForecastLocation', ADDON.getSetting('ForecastLocation'))#@UndefinedVariable
    WINDOW.setProperty('RegionalLocation', ADDON.getSetting('RegionalLocation'))#@UndefinedVariable
    WINDOW.setProperty('Location1', ADDON.getSetting('ForecastLocation'))#@UndefinedVariable
    WINDOW.setProperty('Locations', '1')#@UndefinedVariable

    #Explicitly set unused flags to false, so there are no unusual side
    #effects/residual data when moving from another weather provider.
    WINDOW.setProperty('36Hour.IsFetched', '')#@UndefinedVariable
    WINDOW.setProperty('Weekend.IsFetched', '')#@UndefinedVariable
    WINDOW.setProperty('Map.IsFetched', '')#@UndefinedVariable
    WINDOW.setProperty('Weather.CurrentView', '')#@UndefinedVariable

if __name__ == '__main__':
    main()
