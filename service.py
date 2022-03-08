import xbmc, xbmcaddon, xbmcgui
import sys
import time

from threading import Thread
import datetime
import time

ServiceStop = ''
#kodi-send --action='Weather.Refresh()'

def restart_service_monitor():
    if ServiceStarted == 'True':
        while ServiceStop == '':
            self.xbmc_monitor.waitForAbort(1)
        #wait_for_property('ServiceStop', value='True', set_property=True)  # Stop service
    #wait_for_property('ServiceStop', value=None)  # Wait until Service clears property
    while ServiceStop != '':
        self.xbmc_monitor.waitForAbort(1)
    Thread(target=ServiceMonitor().run).start()

 
class CronJobMonitor(Thread):
    def __init__(self, update_hour=0):
        Thread.__init__(self)
        ServiceStarted = 'False'
        ServiceStop = ''
        self.exit = False
        self.poll_time = 600  # Poll every 30 mins since we don't need to get exact time for update
        self.update_hour = update_hour
        self.xbmc_monitor = xbmc.Monitor()

    def weather(self):
        import sys
        import os,sys,inspect
        from pathlib import Path
        currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
        parentdir = str(Path(os.path.dirname(currentdir) + '/weather.metoffice/src'))
        sys.path.insert(0,parentdir) 
        #xbmc.log(str(currentdir)+'===>PHIL', level=xbmc.LOGFATAL)
        #xbmc.log(str(parentdir)+'===>PHIL', level=xbmc.LOGFATAL)
        # insert at 1, 0 is the script path (or '' in REPL)
        import pytz
        from metoffice import default
        from metoffice import utilities, properties, urlcache
        from metoffice.utilities import gettext as _
        from metoffice.constants import WINDOW, ADDON, API_KEY, CURRENT_VIEW, ADDON_DATA_PATH, ADDON_BANNER_PATH
        urlcache.URLCache(ADDON_DATA_PATH).erase()
        default.main()

    def run(self):
        self.next_time = 0

        self.xbmc_monitor.waitForAbort(5)  # Wait 10 minutes before doing updates to give boot time
        if self.xbmc_monitor.abortRequested():
            del self.xbmc_monitor
            return
        """
        first_run_flag = False
        weather_time = xbmcgui.Window(10000).getProperty("weather_time")

        if str(weather_time) == '':
            first_run_flag = True
            xbmc.log(str('weather.metoffice_SLEEP')+'===>PHIL', level=xbmc.LOGFATAL)
            time.sleep(4)
        """

        #import datetime
        #from datetime import datetime

        curr_time = time.time()
        curr_time = datetime.datetime.now().replace(minute=0,second=0, microsecond=0).timestamp()
        """
        weather_time = xbmcgui.Window(10000).getProperty("weather_time")
        xbmc.log(str(curr_time)+'curr_time===>PHIL', level=xbmc.LOGINFO)
        xbmc.log(str(weather_time)+'weather_timecurr_time===>PHIL', level=xbmc.LOGINFO)
        if str(weather_time) == '':
            curr_time = datetime.datetime.now().replace(minute=0,second=0, microsecond=0).timestamp()
            xbmcgui.Window(10000).setProperty("weather_time", str(curr_time))
        elif curr_time > float(weather_time) + 60*60:
            curr_time = datetime.datetime.now().replace(minute=0,second=0, microsecond=0).timestamp()
            xbmcgui.Window(10000).setProperty("weather_time", str(curr_time))
        else:
            #exit()
            print('DO NOT EXIT')
        """
        xbmcgui.Window(10000).setProperty("weather_time", str('True'))
        self.weather()
        xbmcgui.Window(10000).setProperty("weather_time", str('False'))
        self.next_time = float(curr_time) + 60*60
        #if first_run_flag == True:
        #    time.sleep(2.5)
        #    xbmc.log(str('weather.metoffice_SLEEP')+'===>PHIL', level=xbmc.LOGFATAL)


        xbmc.log(str('CronJobMonitor_STARTED_WEATHER')+'===>___OPEN_INFO', level=xbmc.LOGINFO)
        while not self.xbmc_monitor.abortRequested() and not self.exit and self.poll_time:
            self.curr_time = datetime.datetime.now().replace(minute=0,second=0, microsecond=0).timestamp()
            if int(time.time()) > self.next_time:  # Scheduled time has past so lets update
                library_update_period = 1
                self.next_time = self.curr_time + library_update_period*60*60
                xbmcgui.Window(10000).setProperty("weather_time", str('True'))
                self.weather()
                xbmcgui.Window(10000).setProperty("weather_time", str('False'))
            if self.next_time - int(time.time()) < 3540:
                self.poll_time = int(self.next_time - int(time.time())) + 10
            else:
                self.poll_time = 70
            #xbmc.log(str(self.poll_time)+'self.poll_time)===>PHIL', level=xbmc.LOGINFO)
            self.xbmc_monitor.waitForAbort(self.poll_time)

        del self.xbmc_monitor


class ServiceMonitor(object):
    def __init__(self):
        xbmc.log(str('ServiceMonitor_diamond_info_service_started')+'===>___OPEN_INFO', level=xbmc.LOGINFO)
        xbmc.executebuiltin('Dialog.Close(busydialognocancel)')
        xbmc.executebuiltin('Dialog.Close(busydialog)')
        self.exit = False
        self.cron_job = CronJobMonitor(0)
        self.cron_job.setName('Cron Thread')
        self.player_monitor = None
        self.my_monitor = None
        self.xbmc_monitor = xbmc.Monitor()

    def _on_clear(self):
        """
        IF we've got properties to clear lets clear them and then jump back in the loop
        Otherwise we should sit for a second so we aren't constantly polling
        """
        #if self.listitem_monitor.properties or self.listitem_monitor.index_properties:
        #    return self.listitem_monitor.clear_properties()
        #self.listitem_monitor.blur_fallback()
        self.xbmc_monitor.waitForAbort(1)

    def _on_exit(self):
        if not self.xbmc_monitor.abortRequested():
            #self.listitem_monitor.clear_properties()
            ServiceStarted = ''
            ServiceStop = '' 
        #del self.player_monitor
        #del self.listitem_monitor
        del self.xbmc_monitor

    def poller(self):
        while not self.xbmc_monitor.abortRequested() and not self.exit:
            if ServiceStop == 'True' :
                self.cron_job.exit = True
                self.exit = True

            # Otherwise just sit here and wait
            else:
                self._on_clear()

        # Some clean-up once service exits
        self._on_exit()

    def run(self):
        xbmc.log(str('waether_service_started')+'===>___OPEN_INFO', level=xbmc.LOGINFO)
        ServiceStarted = 'True'
        self.cron_job.start()
        self.poller()

if __name__ == '__main__':
    ServiceMonitor().run()
