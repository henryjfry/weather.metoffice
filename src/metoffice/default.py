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
import xbmcvfs
import xbmcgui
import xbmcaddon
import sys
import time
import json

if 'info=' in str(sys.argv):
	if 'setup_settings_xml' in str(sys.argv[1]):
		import xml.etree.cElementTree as ET
		import requests
		response = requests.get('http://api.geoiplookup.net/')
		tree = ET.fromstring(response.text)
		tree = ET.ElementTree(tree)
		root = tree.getroot()
		for child in root:
			for result in child:
					for i in result:
						if i.tag == 'longitude':
							longitude = float(i.text)
						if i.tag == 'latitude':
							latitude = float(i.text)

		#latitude1 = xbmcgui.Dialog().input(heading='Latitude (Before Decimal Point)', type=xbmcgui.INPUT_NUMERIC)
		#latitude2 = xbmcgui.Dialog().input(heading='Latitude (After D.P) = %s.xxx' % (str(latitude1)), type=xbmcgui.INPUT_NUMERIC)
		#lat_sign = xbmcgui.Dialog().yesno('Positive/Negative Latitude', 'Positive/Negative', nolabel='+ve' ,yeslabel='-ve')
		#latitude = float(str(latitude1) + '.' + str(latitude2))
		#if not lat_sign:
		#	latitude = latitude * -1
		#longitude1 = xbmcgui.Dialog().input(heading='Longitude (Before Decimal Point)', type=xbmcgui.INPUT_NUMERIC)
		#longitude2 = xbmcgui.Dialog().input(heading='Longitude (After D.P) = %s.xxx' % (str(longitude1)), type=xbmcgui.INPUT_NUMERIC)
		#long_sign = xbmcgui.Dialog().yesno('Positive/Negative Longitude', 'Positive/Negative', nolabel='+ve' ,yeslabel='-ve')
		#longitude = float(str(longitude1) + '.' + str(longitude2))
		#if not long_sign:
		#	longitude = longitude * -1

		import setup_xml
		ADDON = xbmcaddon.Addon(id="weather.metoffice")
		#https://register.metoffice.gov.uk/MyAccountClient/account/view
		API_KEY = ADDON.getSetting('ApiKey')
		xml_path = xbmcvfs.translatePath("special://profile/addon_data/"+'weather.metoffice/settings.xml')
		return_var = setup_xml.setup_xml(api_key=API_KEY, latitude=latitude,longitude=longitude,xml_path=xml_path)
		#xbmc.log(str(return_var)+'_weather.metoffice===>setup_settings_xml', level=xbmc.LOGINFO)
		ADDON.setSetting('ApiKey', API_KEY)
		weather_time = 'False'

weather_time = xbmcgui.Window(10000).getProperty("weather_time")

window_id = xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"GUI.GetProperties","params":{"properties":["currentwindow", "currentcontrol"]},"id":1}')
window_id = json.loads(window_id)

if 'Weather' in str(window_id):
    weather_time = 'True'

if weather_time == 'False':
    exit()

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
    screen_saver = xbmc.getCondVisibility("System.ScreenSaverActive")
    if str(screen_saver) == str('True'):
        xbmc.executebuiltin('ActivateWindow(%s)' % xbmcgui.getCurrentWindowId())
        xbmc.executeJSONRPC('{"jsonrpc": "2.0", "id": 1, "method": "Input.Select"}')

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
