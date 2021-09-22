from __future__ import absolute_import
from __future__ import print_function

import signal, os, time, string, pickle, re, sys, glob
import traceback

# Get a list of ports
def serial_ports():

    """ Lists serial port names
        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """

    ports = []
    if sys.platform.startswith('win'):
        ports2 = serial.tools.list_ports.comports()
        for aa in ports2:
            ports.append(aa[0])
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        #print("linux")
        ports = glob.glob('/dev/ttyU[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        # rely on serial module
        ports2 = serial.tools.list_ports.comports()
        for aa in ports2:
            ports.append(aa[0])
        #raise EnvironmentError('Unsupported platform')

    #print ("ports", ports)
    result = []
    for port in ports:
        try:
            # no testing performed any more
            #s = serial.Serial(port)
            #s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
            print(sys.exc_info())

    #print ("ports result", result)
    return result


import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GLib
from gi.repository import GObject
from gi.repository import Pango

gi.require_version('PangoCairo', '1.0')
from gi.repository import PangoCairo

class   SerDump(object):

    def __init__(self, self2):

        self.agv = 0
        self.self2 = self2
        #self.self2.children.append(self)

        self.win2 = Gtk.Window(Gtk.WindowType.TOPLEVEL)
        self.win2.set_accept_focus(True)
        #self.win2.set_position(Gtk.WIN_POS_CENTER)
        self.win2.set_events(Gdk.EventMask.ALL_EVENTS_MASK)

        self.alt = 0
        self.win2.set_transient_for(None)
        #self.win2.set_transient_for(self.self2.appwin.mywin)

        try:
            self.win2.set_icon_from_file(get_img_path("agvsim.png"))
        except:
            print("Canot load control icon.", "'agvsim.png'", sys.exc_info())

        fdesc  = Pango.FontDescription().from_string("Arial Bold 24px")
        fdescx = Pango.FontDescription().from_string("Sans Bold 20px")

        self.win2.set_title("Serial Activity Dump.")

        self.win2.set_can_focus(True)
        self.win2.connect("key-press-event", self.area_key)
        self.win2.connect("key-release-event", self.area_key)
        self.win2.connect("delete-event", self.area_destroy)

        #xx = config.conf.sql.get("durcx_%d" % self.agv)
        #yy = config.conf.sql.get("durcy_%d" % self.agv)
        #ww = config.conf.sql.get("durcw_%d" % self.agv)
        #hh = config.conf.sql.get("durch_%d" % self.agv)
        #
        #xxx, yyy, www, hhh = get_disp_size()
        #
        #if not xx and not yy == 0:
        #    if self.agv:
        #        self.win2.move(www - 900, 10)
        #    else:
        #        self.win2.move(www - 900, 10)
        #else:
        #    #print("xx", xx, "yy", yy)
        #    self.win2.move(int(xx), int(yy))
        #
        self.tv = Gtk.TextView()
        self.tvs = Gtk.ScrolledWindow()
        self.tvs.add(self.tv)

        self.tv2 = Gtk.TextView()
        self.tvs2 = Gtk.ScrolledWindow()
        self.tvs2.add(self.tv2)

        self.tv3 = Gtk.TextView()
        self.tvs3 = Gtk.ScrolledWindow()
        self.tvs3.add(self.tv3)

        self.tv4 = Gtk.TextView()
        self.tvs4 = Gtk.ScrolledWindow()
        self.tvs4.add(self.tv4)

        self.tv5 = Gtk.TextView()
        self.tvs5 = Gtk.ScrolledWindow()
        self.tvs5.add(self.tv5)

        vbox4 = Gtk.VBox()
        vbox4.set_border_width(4)
        vbox4.pack_start(Gtk.Label("AGV 1"), 0, 0, 2)
        vbox4.pack_start(self.tvs, 1, 1, 2)
        vbox4.pack_start(Gtk.Label("AGV 2"), 0, 0, 2)
        vbox4.pack_start(self.tvs2, 1, 1, 2)
        vbox4.pack_start(Gtk.Label("AGV 3"), 0, 0, 2)
        vbox4.pack_start(self.tvs3, 1, 1, 2)
        vbox4.pack_start(Gtk.Label("AGV 4"), 0, 0, 2)
        vbox4.pack_start(self.tvs4, 1, 1, 2)
        vbox4.pack_start(Gtk.Label("AGV 5"), 0, 0, 2)
        vbox4.pack_start(self.tvs5, 1, 1, 2)

        self.win2.set_size_request(500, 600)
        self.win2.add(vbox4)

        self.win2.show_all()
        self.win2.activate_focus()

    def clean(self, txt):
        ret = ""
        for aa in txt:
            if aa.isalnum() or aa.isspace() or aa.find("-<>+=_-"):
                #or aa.find("!@#$%^&*_+-=;':<>,."):
                ret += aa
        return ret

    # Append to text view what serial port received info
    def append_tv(self, num, txt):

        txt2 = self.clean(txt)
        tvx = None;
        if num == 0: tvx = self.tv
        if num == 1: tvx = self.tv2
        if num == 2: tvx = self.tv3
        if num == 3: tvx = self.tv4
        if num == 4: tvx = self.tv5

        if tvx == None:
            print("Buffer number limit exceeded", num)
            return

        #print("serdump", num, txt)

        tbuff = tvx.get_buffer()
        iii = tbuff.get_end_iter()
        tbuff.insert(iii, txt2);
        process_events()
        vadj = tvx.get_vadjustment()
        vadj.set_value(vadj.get_upper())

    def close(self):
        #print ("called serdump close")
        self.win2.close()
        pass

    # Call key handler
    def area_key(self, area, event):
        if  event.type == Gdk.EventType.KEY_PRESS:

            if event.keyval == Gdk.KEY_Alt_L or \
                  event.keyval == Gdk.KEY_Alt_R:
                self.alt = True;

            if event.keyval == Gdk.KEY_x or \
                    event.keyval == Gdk.KEY_X:
                if self.alt:
                    #self.self2.appwin.mywin.present()
                    pass

        elif  event.type == Gdk.EventType.KEY_RELEASE:
            if event.keyval == Gdk.KEY_Alt_L or \
                  event.keyval == Gdk.KEY_Alt_R:
                self.alt = False;


    def area_destroy(self, event, arg):

        #print("serdump area destroy", self)

        # Finally, gdk delivers an up to date position
        oldxx, oldyy = self.win2.get_position()
        oldww, oldhh = self.win2.get_size()

        #print ("save coord", oldxx, oldyy, oldww, oldhh)
        #print ("save coord2", self.win2.get_window().get_geometry())

        #config.conf.sql.put("durcx_%d" % self.agv, oldxx)
        #config.conf.sql.put("durcy_%d" % self.agv, oldyy)
        #config.conf.sql.put("durcw_%d" % self.agv, oldww)
        #config.conf.sql.put("durch_%d" % self.agv, oldhh)

def print_exception(xstr):
    cumm = xstr + " "
    a,b,c = sys.exc_info()
    if a != None:
        cumm += str(a) + " " + str(b) + "\n"
        try:
            #cumm += str(traceback.format_tb(c, 10))
            ttt = traceback.extract_tb(c)
            for aa in ttt:
                cumm += "File: " + os.path.basename(aa[0]) + \
                        " Line: " + str(aa[1]) + "\n" +  \
                    "   Context: " + aa[2] + " -> " + aa[3] + "\n"
        except:
            print("Could not print trace stack. ", sys.exc_info())
    print(cumm)

def process_events():

    got_clock = time.time() + float(5) / 1000
    #print got_clock
    try:
        while True:
            if time.time() > got_clock:
                break
            Gtk.main_iteration_do(False)
    except:
        pass


# EOF