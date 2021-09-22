#!/usr/bin/env python3

from __future__ import absolute_import
from __future__ import print_function

import signal, os, sys, time, string, pickle, re, serial
import traceback

import serial.tools.list_ports as port_list

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GLib
from gi.repository import GObject
from gi.repository import Pango

gi.require_version('PangoCairo', '1.0')
from gi.repository import PangoCairo

from ser_utils import *

def OnExit(arg):
    Gtk.main_quit()

class   MainWin(Gtk.Window):

    def __init__(self, item = 0):

        Gtk.Window.__init__(self)

        self.set_accept_focus(True)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_events(Gdk.EventMask.ALL_EVENTS_MASK)
        self.set_transient_for(self)
        try:
            self.set_icon_from_file("pmcser.png")
        except:
            print("Canot load icon.", "'pmcser.png'")

        self.set_can_focus(True)
        self.connect("key-press-event", self.area_key)
        self.connect("key-release-event", self.area_key)
        self.connect("focus-in-event", self.area_focus)
        self.connect("delete-event", self.area_destroy)
        self.connect("unmap", OnExit)
        self.set_size_request(600, 800)
        self.set_title("PMC Serial utility")
        self.main = Decor()
        self.add(self.main)
        self.show_all()

    def area_destroy(self, event, arg):

        #print("decor area destroy", self.item)

        # Finally, gdk delivers an up to date position
        oldxx, oldyy = self.get_position()
        oldww, oldhh = self.get_size()

        #print ("decore save coord item_%d" % self.item, oldxx, oldyy, oldww, oldhh)
        #config.conf.sql.put("wsrcx_%d" % self.item, oldxx)
        #config.conf.sql.put("wsrcy_%d" % self.item, oldyy)
        #config.conf.sql.put("wsrcw_%d" % self.item, oldww)
        #config.conf.sql.put("wsrch_%d" % self.item, oldhh)

    # Focus on the current window
    def area_focus(self, area, event):
        #print ("decor area_focus")
        pass

    # Call key handler
    def area_key(self, area, event):
        #print ("decor area_key", event)
        # Do key down:
        if  event.type == Gdk.EventType.KEY_PRESS:
            if event.keyval == Gdk.KEY_Escape:
                #print "Esc"
                area.destroy()

        if  event.type == Gdk.EventType.KEY_PRESS:
            if event.keyval == Gdk.KEY_Return:
                #print "Ret"
                area.destroy()

            if event.keyval == Gdk.KEY_Alt_L or \
                    event.keyval == Gdk.KEY_Alt_R:
                self.alt = True;

            if event.keyval >= Gdk.KEY_1 and \
                    event.keyval <= Gdk.KEY_9:
                pass
                print("pedwin Alt num", event.keyval - Gdk.KEY__1)

            if event.keyval == Gdk.KEY_x or \
                    event.keyval == Gdk.KEY_X:
                if self.alt:
                    #self.self2.appwin.mywin.present()
                    #area.destroy()
                    pass

        elif  event.type == Gdk.EventType.KEY_RELEASE:
            if event.keyval == Gdk.KEY_Alt_L or \
                  event.keyval == Gdk.KEY_Alt_R:
                self.alt = False;

class SerWin(Gtk.VBox):

    def __init__(self, self2):

        Gtk.VBox.__init__(self)
        self.self2 = self2
        frame = Gtk.Frame()
        #frame.modify_bg(Gtk.StateType.NORMAL, Gdk.Color(0, 32000, 0))
        #frame.set_border_width(10)
        frame.set_margin_left(10); frame.set_margin_right(10)

        frame.set_label(" Serial")
        self.self2.fill_combo()
        self.self2.name_combo = Gtk.ComboBox.new_with_model_and_entry(self.self2.name_store)
        self.self2.name_combo.connect("changed", self.self2.combo_changed)
        self.self2.name_combo.set_entry_text_column(1)
        self.self2.name_combo.set_active_id(None)
        label_combo = Gtk.Label.new("Associated COM Port:");
        self.self2.comstat = Gtk.Label.new("Com Status: None");
        vbox = Gtk.VBox()
        vbox.pack_start(label_combo, 0, 0, 4)
        vbox.pack_start(self.self2.name_combo, 0, 0, 4)
        vbox.pack_start(self.self2.comstat, 0, 0, 4)
        vbox.pack_start(self.self2.but1, 0, 0, 4)
        frame.add(vbox)
        self.pack_start(frame, 0, 0, 0)

class Info(Gtk.VBox):

    def __init__(self, item = 0):
        Gtk.VBox.__init__(self)
        frame = Gtk.Frame()
        #frame.set_border_width(10)
        frame.set_margin_left(10); frame.set_margin_right(10)

        frame.set_label(" Info ")
        #frame.set_shadow_type(Gtk.ShadowType.ETCHED_IN )
        #frame.modify_bg(Gtk.StateType.NORMAL, Gdk.Color(0, 100, 0))
        label3a = Gtk.Label.new(" ");
        label4a = Gtk.Label.new(" ");
        #self.label_1 = Gtk.Label.new(" NO INFO  ");
        fdesc  = Pango.FontDescription().from_string("Arial Bold 24px")
        fdescs = Pango.FontDescription().from_string("Arial Bold 18px")

        grid = Gtk.Grid(); grid.set_column_homogeneous(True);

        for aa in range(8):
            lab = Gtk.Label.new("Cnt-" + str(aa+1))
            lab.override_font(fdesc)
            lab.set_xalign(0.5)
            #lab.modify_bg(Gtk.StateType.NORMAL, Gdk.Color(0, 32000, 0))
            grid.attach(lab, aa, 1, 1, 1)
        self.labarr = []
        for aa in range(8):
            lab = Gtk.Label.new("0")
            lab.override_font(fdescs)
            lab.set_xalign(0.5)
            self.labarr.append(lab)
            #lab.modify_bg(Gtk.StateType.NORMAL, Gdk.Color(0, 30535, 0))
            grid.attach(lab, aa, 2, 1, 1)

        # Spacer
        for aa in range(8):
            lab = Gtk.Label.new(" ")
            grid.attach(lab, aa, 3, 1, 1)

        for aa in range(8):
            lab = Gtk.Label.new("Dur-" + str(aa+1   ))
            lab.override_font(fdesc)
            lab.set_xalign(0.5)
            grid.attach(lab, aa, 4, 1, 1)

        self.labarr2 = []
        for aa in range(8):
            lab = Gtk.Label.new("0")
            lab.override_font(fdescs)
            lab.set_xalign(0.5)
            self.labarr2.append(lab)
            grid.attach(lab, aa, 5, 1, 1)

        for aa in range(8):
            lab = Gtk.Label.new("")
            grid.attach(lab, aa, 6, 1, 1)

        for aa in range(4):
            lab = Gtk.Label.new("Input-" + str(aa+1))
            lab.override_font(fdesc)
            lab.set_xalign(0.5)
            grid.attach(lab, aa * 2, 7, 2, 1)

        self.labarr3 = []
        for aa in range(4):
            lab = Gtk.Label.new("0")
            lab.override_font(fdescs)
            lab.set_xalign(0.5)
            self.labarr3.append(lab)
            grid.attach(lab, aa * 2, 8, 2, 1)

        for aa in range(8):
            lab = Gtk.Label.new("")
            grid.attach(lab, aa, 9, 1, 1)

        for aa in range(2):
            lab = Gtk.Label.new("Temp-" + str(aa+1))
            lab.override_font(fdesc)
            lab.set_xalign(0.5)
            grid.attach(lab, aa * 4, 10, 4, 1)

        self.labarr4 = []
        for aa in range(2):
            lab = Gtk.Label.new("0")
            lab.override_font(fdescs)
            lab.set_xalign(0.5)
            self.labarr4.append(lab)
            grid.attach(lab, aa * 4, 11, 4, 1)

        for aa in range(8):
            lab = Gtk.Label.new(" ")
            grid.attach(lab, aa, 12, 1, 1)

        for aa in range(4):
            lab = Gtk.Label.new("Ala-" + str(aa+1))
            lab.override_font(fdesc)
            lab.modify_fg(Gtk.StateType.NORMAL, Gdk.Color(0, 0, 32000))
            lab.set_xalign(0.5)
            grid.attach(lab, aa * 2, 13, 2, 1)

        self.labarr5 = []
        for aa in range(4):
            lab = Gtk.Label.new("0")
            lab.override_font(fdescs)
            lab.set_xalign(0.5)
            lab.modify_fg(Gtk.StateType.NORMAL, Gdk.Color(0, 0, 32000))
            self.labarr5.append(lab)
            grid.attach(lab, aa * 2, 14, 2, 1)

        vbox3 = Gtk.VBox()
        vbox3.pack_start(label3a, 0, 0, 0)
        vbox3.pack_start(grid, 1, 1, 0)
        vbox3.pack_start(label4a, 0, 0, 0)
        frame.add(vbox3)

        self.add(frame)


class   Decor(Gtk.VBox):

    def __init__(self, item = 0):

        Gtk.VBox.__init__(self)
        self.item = item
        #self.self2 = self2
        self.timeout = 300
        self.lastser = time.time()
        self.closing = 0
        self.accum = ""
        self.old_str = ""
        #self.serdump = SerDump(None)
        print("Loading decor")

        self.sname = "serial%d" % self.item
        self.serial_device = None

        fdescx = Pango.FontDescription().from_string("Sans Bold 20px")

        frame2 = Gtk.Frame()
        #frame2.set_border_width(10)
        frame2.set_margin_left(10); frame2.set_margin_right(10)
        frame2.set_label(" Flow Control ")
        label3 = Gtk.Label.new("   ");   label4 = Gtk.Label.new("   ")

        mmm = "     Com       Z#       Arg1       Arg2 "
        #ddd = " \  ##  ##  ##  ##  "
        ddd = " \  00  00  00  00  "

        label5 = Gtk.Label.new("   ");  label6 = Gtk.Label.new(" item Send to  Radio ")
        label6a = Gtk.Label.new(mmm)

        self.sserial = Gtk.Label.new(ddd);  label8 = Gtk.Label.new("   ")
        self.sserial.override_font(fdescx)

        label9 = Gtk.Label.new(" item Receive from  Radio ");  label10 = Gtk.Label.new("   ")
        label9a = Gtk.Label.new(mmm)
        self.rserial = Gtk.Label.new(ddd);
        self.rserial.override_font(fdescx)

        self.tv = Gtk.TextView()
        #self.tv.set_size_request(70, 50)

        self.tvs = Gtk.ScrolledWindow()
        self.tvs.add(self.tv)

        self.but1  = Gtk.Button.new_with_mnemonic("    Disconnect  ");
        self.but1.connect("clicked", self.but1_pressed);

        self.but_clear  = Gtk.Button.new_with_mnemonic("    Clear Window  ");
        self.but_clear.connect("clicked", self.but_clear_pressed);

        self.but_exit  = Gtk.Button.new_with_mnemonic("    E_xit App  ");
        self.but_exit.connect("clicked", self.but_exit_pressed);

        self.hbox3 = Gtk.HBox()
        self.but2  = Gtk.Button.new_with_mnemonic("    Send Stat Command  ");
        self.but2.connect("clicked", self.but2_pressed);
        self.hbox3.pack_start(self.but2, 1, 1, 0)
        self.hbox3.pack_start(Gtk.Label.new(" Auto Query: "), 0, 0, 2)
        self.checkauto = Gtk.CheckButton()
        self.checkauto.connect("toggled", self.toggled)
        self.checkauto.set_active(True)

        self.hbox3.pack_start(self.checkauto, 0, 0, 4)

        self.but4  = Gtk.Button.new_with_mnemonic("    Send Verbose Command  ");
        self.but4.connect("clicked", self.but4_pressed);

        entry = Gtk.Entry();
        hbox2 = Gtk.HBox()
        hbox2.pack_start(label3, 0, 0, 0)
        hbox2.pack_start(entry, True, True, 0)
        hbox2.pack_start(label4, 0, 0, 0)

        vbox4 = Gtk.VBox()
        vbox4.pack_start(self.tvs, 1, 1, 2)
        vbox4.pack_start(self.hbox3, 0, 0, 2)
        vbox4.pack_start(self.but4, 0, 0, 2)
        vbox4.pack_start(self.but_clear, 0, 0, 2)
        vbox4.pack_start(self.but_exit, 0, 0, 2)

        self.ser = SerWin(self)

        frame2.add(vbox4)
        self.info = Info()

        vbox2 = Gtk.VBox()
        vbox2.pack_start(self.ser, 0, 0, 0)
        vbox2.pack_start(self.info, 0, 0, 0)
        vbox2.pack_start(frame2, 1, 1, 0)

        #xx = config.conf.sql.get("wsrcx_%d" % self.item)
        #yy = config.conf.sql.get("wsrcy_%d" % self.item)
        #ww = config.conf.sql.get("wsrcw_%d" % self.item)
        #hh = config.conf.sql.get("wsrch_%d" % self.item)
        xx = 0; yy = 0; ww = 0; hh = 0

        #if not xx and not ww:
        #    xxx, yyy, www, hhh = get_disp_size()
        #    if item:
        #        self.win2.move(www - 300, 10)
        #    else:
        #        self.win2.move(www - 600, 10)
        #else:
        #    #print("xx", xx, "yy", yy)
        #    self.win2.move(int(xx), int(yy))

        self.worker = Worker(self, 50)
        self.pack_start(vbox2, 1, 1, 0)

    def toggled(self, but):
        #print("toggled")
        if self.checkauto.get_active():
            GLib.timeout_add(2000, self.auto_handler_tick)


    def clean_str(self, txt):
        ret = ""
        for aa in txt:
            if aa.isalnum() or aa.isspace() or aa.find("-=_+<>"):
                #or aa.find("!@#$%^&*_+-=;':<>,."):
                ret += aa
        return ret

    # Append to serial port receive info
    def append_tv(self, txt):
        tbuff = self.tv.get_buffer()
        # To big?
        sss = tbuff.get_start_iter(); eee = tbuff.get_end_iter()
        ttt = tbuff.get_text(sss, eee, False)
        if len(ttt) > 2000:
            #print("cutting", ttt)
            ooo = tbuff.get_iter_at_offset(500)
            tbuff.delete(sss, eee)

        iii = tbuff.get_end_iter()
        tbuff.insert(iii, txt)
        process_events()
        vadj = self.tv.get_vadjustment()
        vadj.set_value(vadj.get_upper())

    def clear_tv(self):
        tbuff = self.tv.get_buffer()
        sss =  tbuff.get_start_iter()
        iii = tbuff.get_end_iter()
        tbuff.delete(sss, iii)

    def fill_combo(self):
        # Add port selection COMBO BOX
        #self.ports = list(port_list.comports())
        self.name_store = Gtk.ListStore(int, str)
        self.ports = list(serial_ports())
        print ("serial ports:", self.ports)
        nn = 0
        for aa in self.ports:
            self.name_store.append([nn, aa])
            nn += 1

    def but1_pressed(self, but):
        #print ("but pressed")
        if self.serial_device:
            #process_events()
            self.serial_device.reset_input_buffer()
            self.serial_device.close()
            self.name_combo.SelectedIndex = -1;
            self.serial_device = None
            self.name_combo.set_active_id(None)
            self.comstat.set_text("Disconnected.")
        else:
            self.comstat.set_text("Not connected, cannot disconnect.")

    def but2_pressed(self, but):
        #print ("but pressed")
        if not self.serial_device:
            print("No serial")
            self.comstat.set_text("No serial connection")
            return
        self.send_serial("stat\r")

    def but4_pressed(self, but):
        #print ("but pressed")
        if not self.serial_device:
            print("No serial")
            self.comstat.set_text("No serial connection")
            return
        self.send_serial("verbose 2\r")

    def but_clear_pressed(self, but):
        #print ("but pressed")
        self.clear_tv()

    def but_exit_pressed(self, but):
        #print ("but pressed")

        if self.serial_device:
            self.but1_pressed( None)
        OnExit(0)
        pass

# --------------------------------------------------------------------

    def combo_changed(self, combo):

        tree_iter = combo.get_active_iter()
        if tree_iter is not None:
            model = combo.get_model()
            row_id, pname = model[tree_iter][:2]
            #print("Combo Selected: ID=%d, name='%s'" % (row_id, pname))
            try:
                #self.ports = list(port_list.comports())
                #print("ports", self.ports)
                #pp = string.split(str(self.ports[row_id]))[0]
                print ("Serial port found: '%s'" % pname)

                # Note only this baud rate is supported
                self.serial_device = serial.Serial(pname, 115200, timeout=0)
                #print(self.serial_device)
                self.comstat.set_text("Connected to port: " +  pname)

                #GLib.timeout_add(self.timeout, self.handler_tick)
                self.worker.restart_timer()

                if self.checkauto.get_active():
                    GLib.timeout_add(2000, self.auto_handler_tick)

            except:
                print_exception("serial");
                #print ("Serial port NOT found: '%s'" % name)
                self.serial_device = None

            if not self.serial_device:
                print("Cannot open serial port", name)
                self.comstat.set_text("Error on setting port: " +  pname)
                pass
        else:
            entry = combo.get_child()
            print("Entered: %s" % entry.get_text())

    def close(self):
        if not self.serial_device:
            return
        self.closing = 1
        process_events()
        self.serial_device.reset_input_buffer()
        process_events()
        self.serial_device.close()

    # Auto start item
    def auto_handler_tick(self):
        if self.serial_device:
            try:
                self.send_serial("stat\n")
            except:
                pass

            if self.checkauto.get_active():
                GLib.timeout_add(2000, self.auto_handler_tick)

    def send_serial(self, strx):
        if self.serial_device:
            #print("Sending", strx)
            for aa in strx:
                #print("send", aa, ord(aa))
                stry = aa.encode("cp437")
                self.serial_device.write(stry)
            time.sleep(0.2)

    # --------------------------------------------------------------------
    # Evaluate string from  simulation

    def got_string(self, strx):

        #print("got_str", "'" + strx + "'")
        # Interpret only once
        if self.old_str == strx:
            return
        self.old_str = strx
        strx3 = strx.replace("\r",  "")
        strx3 = strx3.replace("\n", "")
        # Nothing ... do nothing
        if not strx3 or strx3 == "":
            return
        #print ("Got string '%s'" % strx3)
        arrx = strx3.split()
        #print("arrx", arrx)
        try:
            if arrx[0] == 'Counter':
                idx = int(arrx[1])
                self.info.labarr[idx-1].set_text(arrx[3])
                self.info.labarr2[idx-1].set_text(arrx[5])

            elif arrx[0] == 'Input':
                idx = int(arrx[1])
                self.info.labarr3[idx-1].set_text(arrx[3])

            elif arrx[0] == 'Probe':
                idx = int(arrx[1])
                if arrx[3] == "-100.0000":
                    self.info.labarr4[idx-1].set_text("Probe?")
                else:
                    self.info.labarr4[idx-1].set_text(arrx[3])

            elif arrx[0] == 'Relay':
                idx = int(arrx[1])
                self.info.labarr5[idx-1].set_text(arrx[3])

            else:
                # Ignore non matches
                pass
        except:
            print("exc at", arrx, sys.exc_info())
            pass

class Worker():

    def __init__(self, self2, timeout):
        self.timeout = timeout
        self.restart_timer();
        self.self2 = self2
        self.sema = False           # Not critical, just prevent pileup
        pass

    # This handler will pump all the serial data back to the system
    def handler_tick(self):

        # No need to work any more
        if self.self2.closing:
            return
        if not self.self2.serial_device:
            return
        if self.sema:
            print("oops ... semaphore return")
            return

        self.sema = True
        #print ("In hadler tick, got serial port\n", self.self2.serial_device)
        curr = self.self2.serial_device.inWaiting()
        #print("curr", curr)
        if curr > 0:
            #self.lastser = time.time()
            got = self.self2.serial_device.read(curr)
            #print("curr", curr, "got", len(got))
            gotstr = got.decode("cp437")
            self.self2.append_tv(gotstr)
            #print("gotstr: '", gotstr, "'")

            self.self2.accum = self.self2.accum + gotstr
            #print ("got data", self.self2.accum)

            # Frame the line
            while(True):
                fff2 = str(self.self2.accum).find("\r")
                fff3 = str(self.self2.accum).find("\n")
                fff4 = max(fff2, fff3)
                if fff4 >= 0:
                    # Got a return
                    laststr = self.self2.accum[0:fff4]
                    self.self2.got_string(laststr)
                    # Cut out what is processed
                    self.self2.accum =  self.self2.accum[fff4+1:]
                else:
                    break
        self.sema = False
        self.restart_timer()

    def restart_timer(self):
        GLib.timeout_add(self.timeout, self.handler_tick)

if __name__ == '__main__':

    global mainwin
    print(sys.argv)
    mainwin = MainWin()
    Gtk.main()

# EOF