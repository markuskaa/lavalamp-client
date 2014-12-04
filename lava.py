import urllib2
import concurrent.futures
import logging
import ConfigParser
import wx

logging.basicConfig()

#URL = 'http://svr-dev-20:8080/?cmd=isGlowing'
LAMP_ON = '1'
LAMP_OFF = '0'
LAMP_UNDEFINED = '?'
UNDEFINED_STATE = [LAMP_UNDEFINED, 'Getting invalid response(s) from server']

OK_ICON = 'data\\ok.png'
FAIL_ICON = 'data\\fail.png'
WARN_ICON = 'data\\warn.png'

CONFIG_FILE = 'data\\lava.cfg'
MAIN_SECTION = 'Main'
TIMER_INTERVAL_KEY = 'timer_interval'
URL_KEY = 'url'

config = ConfigParser.RawConfigParser()
config.read(CONFIG_FILE)

def get_latest_status():
    print ("getting latest status")
    #raise Exception()
    content = urllib2.urlopen(config.get(MAIN_SECTION, URL_KEY)).read()
    status = content.split('|')
    if ((status[0] == LAMP_ON or status[0] == LAMP_OFF) and len(status) == 2):
        return status
    else:
        print 'Invalid response: ' + content
        return UNDEFINED_STATE

        



def create_menu_item(menu, label, func):
    item = wx.MenuItem(menu, -1, label)
    menu.Bind(wx.EVT_MENU, func, id=item.GetId())
    menu.AppendItem(item)
    return item


class TaskBarIcon(wx.TaskBarIcon):
    def __init__(self):
        super(TaskBarIcon, self).__init__()
        self.timer = wx.Timer(self)
        #self.set_icon(OK_ICON)
        self.Bind(wx.EVT_TIMER, self.on_timer, self.timer)
        self.Bind(wx.EVT_TASKBAR_LEFT_DOWN, self.on_left_down)
        self.timer.Start(config.getint(MAIN_SECTION, TIMER_INTERVAL_KEY))
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)
        self.current_future = None
        self.current_state = ['','']
        self.change_state(UNDEFINED_STATE)
        self.change_state(get_latest_status())

    def CreatePopupMenu(self):
        menu = wx.Menu()
        create_menu_item(menu, 'Exit', self.on_exit)
        return menu

    def set_icon(self, path, tooltip):
        icon = wx.IconFromBitmap(wx.Bitmap(path))
        self.SetIcon(icon, tooltip)

    def on_exit(self, event):
        wx.CallAfter(self.Destroy)

    def on_timer(self, event):
        self.run_async()

    def run_async(self):
        future = self.executor.submit(get_latest_status)
        def func(future):
            wx.CallAfter(self.on_new_result, future)
        future.add_done_callback(func)
    
    def on_left_down(self, event):
        self.run_async()

    def change_state(self, new_state):
        #print("new state: "+new_state)
        if (new_state[0] == self.current_state[0]):
            return
        if (new_state[0] == LAMP_OFF):
            self.set_icon(OK_ICON, new_state[1])
            self.ShowBalloon("Build OK", new_state[1], 0, wx.ICON_INFORMATION)
        elif (new_state[0] == LAMP_ON):
            self.set_icon(FAIL_ICON, new_state[1])
            self.ShowBalloon("Build failed", new_state[1], 0, wx.ICON_ERROR)
        else:
            new_state = UNDEFINED_STATE
            self.set_icon(WARN_ICON, new_state[1])
        self.current_state = new_state    
            

    def on_new_result(self, future):
        if future.exception() is not None:
            print("Error getting latest result");
            self.change_state(LAMP_UNDEFINED)
            return
        self.change_state(future.result())
            


def main():
    app = wx.App()
    TaskBarIcon()
    app.MainLoop()


if __name__ == '__main__':
    main()
