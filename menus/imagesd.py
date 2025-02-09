#!/usr/bin/python
# -*- coding: utf-8 -*-

from Plugins.Extensions.ElieSatPanel.menus.Console import Console
import gettext
from Components.Button import Button
from Components.Language import language
from Components.PluginComponent import plugins
from Components.Sources.StaticText import StaticText
from Components.Pixmap import Pixmap
from Components.ActionMap import ActionMap, NumberActionMap
from Components.Sources.List import List
import os
from Plugins.Plugin import PluginDescriptor
from Screens.Standby import TryQuitMainloop
from Screens.MessageBox import MessageBox
from Components.Console import Console as iConsole
from Tools.Directories import fileExists, pathExists, resolveFilename, SCOPE_PLUGINS, SCOPE_LANGUAGE
from types import *
from Components.Label import Label
from Components.MenuList import MenuList
from Screens.PluginBrowser import PluginBrowser
from Screens.Screen import Screen
from Tools.LoadPixmap import LoadPixmap

global min, first_start
min = first_start = 0
####################################

class imagesd(Screen):
	skin = """
<screen name="imagesd" position="0,0" size="1920,1080" backgroundColor="transparent" flags="wfNoBorder" title="ElieSatPanel">
<ePixmap position="0,0" zPosition="-1" size="1920,1080" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ElieSatPanel/images/bglist.png"/>

<!-- title -->
<eLabel text="Download" position="160,120" size="400,50" zPosition="1" font="Regular;40" halign="left" foregroundColor="white" backgroundColor="#ff2c2d2b" transparent="1" />
<ePixmap position="73,125" size="180,47" zPosition="1" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ElieSatPanel/images/1.png" alphatest="blend" />

<!-- title1 -->
<eLabel text="Download" position="1500,700" size="400,50" zPosition="1" font="Regular;40" halign="left" foregroundColor="white" backgroundColor="#ff2c2d2b" transparent="1" />

<!-- title2 -->
<eLabel text="Select and press ok to install" position="1440,790" size="400,50" zPosition="1" font="Bold;27" halign="left" foregroundColor="white" backgroundColor="#ff2c2d2b" transparent="1" />

<!-- minitv -->
<widget source="session.VideoPicture" render="Pig" position="1305,120" size="550,400" zPosition="1" backgroundColor="#ff000000" />

<!-- clock -->
<widget source="global.CurrentTime" render="Label" position="1290,600" size="350,90" font="lsat; 75" noWrap="1" halign="center" valign="bottom" foregroundColor="#11ffffff" backgroundColor="#20000000" transparent="1" zPosition="2">
		<convert type="ClockToText">Default</convert>

<!-- calender -->
</widget>
<widget source="global.CurrentTime" render="Label" position="1530,610" size="335,54" font="lsat; 24" halign="center" valign="bottom" foregroundColor="#11ffffff" backgroundColor="#20000000" transparent="1" zPosition="1">
<convert type="ClockToText">Format %A %d %B</convert>
</widget>

<!-- button -->
<ePixmap position="120,930" zPosition="1" size="240,10" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ElieSatPanel/images/red.png" alphatest="blend" />
<widget source="key_red" render="Label" position="160,870" zPosition="2" size="165,45" font="Regular;35" halign="center" valign="center" backgroundColor="background" foregroundColor="foreground" transparent="1" />
<ePixmap position="400,930" zPosition="1" size="240,10" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ElieSatPanel/images/green.png" alphatest="blend" />
<widget source="key_green" render="Label" position="440,870" zPosition="2" size="165,45" font="Regular;35" halign="center" valign="center" backgroundColor="background" foregroundColor="foreground" transparent="1" />
<ePixmap position="680,930" zPosition="1" size="240,10" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ElieSatPanel/images/yellow.png" alphatest="blend" />
<widget source="key_yellow" render="Label" position="720,870" zPosition="2" size="165,45" font="Regular;35" halign="center" valign="center" backgroundColor="background" foregroundColor="foreground" transparent="1" />
<ePixmap position="960,930" zPosition="1" size="240,10" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ElieSatPanel/images/blue.png" alphatest="blend" />
<widget source="key_blue" render="Label" position="1000,870" zPosition="2" size="165,45" font="Regular;35" halign="center" valign="center" backgroundColor="background" foregroundColor="foreground" transparent="1" />

<!-- menu list -->
<widget source="menu" selectionPixmap="/usr/lib/enigma2/python/Plugins/Extensions/ElieSatPanel/images/selection.png" render="Listbox" position="48,200" size="1240,660" scrollbarMode="showOnDemand" transparent="1">
<convert type="TemplatedMultiContent">
	{"template": [
		MultiContentEntryText(pos = (120, 10), size = (600, 45), font=0, flags = RT_HALIGN_LEFT, text = 0), # index 2 is the Menu Titel
		MultiContentEntryText(pos = (500, 19), size = (700, 35), font=1, flags = RT_HALIGN_LEFT, text = 2), # index 3 is the Description
		MultiContentEntryPixmapAlphaTest(pos = (25, 10), size = (50, 40), png = 3), # index 4 is the pixmap
			],
	"fonts": [gFont("Regular", 35),gFont("Regular", 25)],
	"itemHeight": 66
	}
	</convert>

<!-- info button -->
</widget>
<ePixmap position="1530,870" size="140,60" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ElieSatPanel/images/info.png" zPosition="2" alphatest="blend" />

</screen>"""

	def __init__(self, session):
		self.session = session
		Screen.__init__(self, session)
		self.setTitle(_("ElieSatPanel"))
		self.iConsole = iConsole()
		self.indexpos = None
		self["shortcuts"] = NumberActionMap(["ShortcutActions", "WizardActions", "EPGSelectActions", "NumberActions" "ColorActions", "HotkeyActions"],
		{
			"ok": self.keyOK,
			"cancel": self.exit,
			"back": self.exit,
			"red": self.exit,
			"info": self.infoKey,
			"green": self.keyGreen,
			"yellow": self.keyOK,
			"blue": self.restart,
		})
		self["key_red"] = StaticText(_("Close"))
		self["key_green"] = StaticText(_("Browse"))
		self["key_yellow"] = StaticText(_("Install"))
		self["key_blue"] = StaticText(_("Restart E2"))
		self.list = []
		self["menu"] = List(self.list)
		self.mList()
	def mList(self):
		self.list = []
		a = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/images/1.png"))
		b = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/images/1.png"))
		c = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/images/1.png"))
		d = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/images/1.png"))
		e = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/images/1.png"))
		f = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/images/1.png"))
		g = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/images/1.png"))
		h = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/images/1.png"))
		i = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/images/1.png"))
		j = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/images/1.png"))
		k = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/images/1.png"))
		l = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/images/1.png"))
		m = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/images/1.png"))
		n = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/images/1.png"))
		o = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/images/1.png"))
		p = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/images/1.png"))
		q = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/images/1.png"))
		r = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/images/1.png"))
		s = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/images/1.png"))
		t = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/images/1.png"))
		u = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/images/1.png"))
		v = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/images/1.png"))
		w = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/images/1.png"))
		x = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/images/1.png"))
		y = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/images/1.png"))
		z = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/images/1.png"))
		A = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/images/1.png"))
		B = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/images/1.png"))
		C = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/images/1.png"))
		D = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/images/1.png"))
		E = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/images/1.png"))
		F = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/images/1.png"))
		G = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/images/1.png"))
		H = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/images/1.png"))
		I = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/images/1.png"))
		J = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/images/1.png"))
		K = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/images/1.png"))
		L = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/images/1.png"))
		M = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/images/1.png"))
		N = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/images/1.png"))
		O = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/images/1.png"))

		self.list.append((_("Egami-10.3"), 1, _("تنزيل صور خام من الموقع الرسمي media/hdd or usb or mmc"), a))
		self.list.append((_("Egami-10.4"), 2, _("تنزيل صور خام من الموقع الرسمي media/hdd or usb or mmc"), b))
		self.list.append((_("Egami-10.5"), 3, _("تنزيل صور خام من الموقع الرسمي media/hdd or usb or mmc"), c))
		self.list.append((_("Egami-10.6"), 4, _("تنزيل صور خام من الموقع الرسمي media/hdd or usb or mmc"), d))
		self.list.append((_("Openatv-6.4"), 5, _("تنزيل صور خام من الموقع الرسمي media/hdd or usb or mmc"), e))
		self.list.append((_("Openatv-7.0"), 6, _("تنزيل صور خام من الموقع الرسمي media/hdd or usb or mmc"), f))
		self.list.append((_("Openatv-7.1"), 7, _("تنزيل صور خام من الموقع الرسمي media/hdd or usb or mmc"), g))
		self.list.append((_("Openatv-7.2"), 8, _("تنزيل صور خام من الموقع الرسمي media/hdd or usb or mmc"), h))
		self.list.append((_("Openatv-7.3"), 9, _("تنزيل صور خام من الموقع الرسمي media/hdd or usb or mmc"), i))
		self.list.append((_("Openatv-7.4"), 10, _("تنزيل صور خام من الموقع الرسمي media/hdd or usb or mmc"), j))
		self.list.append((_("Openatv-7.5"), 11, _("تنزيل صور خام من الموقع الرسمي media/hdd or usb or mmc"), k))
		self.list.append((_("Openatv-7.5.1"), 12, _("تنزيل صور خام من الموقع الرسمي media/hdd or usb or mmc"), l))
		self.list.append((_("Openatv-7.6"), 39, _("تنزيل صور خام من الموقع الرسمي media/hdd or usb or mmc"), O))
		self.list.append((_("Openblackhole-4.4"), 13, _("تنزيل صور خام من الموقع الرسمي media/hdd or usb or mmc"), m))
		self.list.append((_("Openblackhole-5.0"), 14, _("تنزيل صور خام من الموقع الرسمي media/hdd or usb or mmc"), n))
		self.list.append((_("Openblackhole-5.1"), 15, _("تنزيل صور خام من الموقع الرسمي media/hdd or usb or mmc"), o))
		self.list.append((_("Openblackhole-5.2"), 16, _("تنزيل صور خام من الموقع الرسمي media/hdd or usb or mmc"), p))
		self.list.append((_("Openblackhole-5.3"), 17, _("تنزيل صور خام من الموقع الرسمي media/hdd or usb or mmc"), q))
		self.list.append((_("Openblackhole-5.4"), 18, _("تنزيل صور خام من الموقع الرسمي media/hdd or usb or mmc"), r))
		self.list.append((_("Openblackhole-5.5.1"), 38, _("تنزيل صور خام من الموقع الرسمي media/hdd or usb or mmc"), N))
		self.list.append((_("Opendroid-7.5"), 19, _("تنزيل صور خام من الموقع الرسمي media/hdd or usb or mmc"), s))
		self.list.append((_("Openhdf-6.5"), 20, _("تنزيل صور خام من الموقع الرسمي media/hdd or usb or mmc"), t))
		self.list.append((_("Openhdf-7.2"), 21, _("تنزيل صور خام من الموقع الرسمي media/hdd or usb or mmc"), u))
		self.list.append((_("Openhdf-7.3"), 22, _("تنزيل صور خام من الموقع الرسمي media/hdd or usb or mmc"), v))
		self.list.append((_("Openpli-7.3"), 23, _("تنزيل صور خام من الموقع الرسمي media/hdd or usb or mmc"), w))
		self.list.append((_("Openpli-8.3"), 24, _("تنزيل صور خام من الموقع الرسمي media/hdd or usb or mmc"), x))
		self.list.append((_("Openpli-9.0"), 25, _("تنزيل صور خام من الموقع الرسمي media/hdd or usb or mmc"), y))
		self.list.append((_("Openpli-9.1"), 26, _("تنزيل صور خام من الموقع الرسمي media/hdd or usb or mmc"), z))
		self.list.append((_("Openpli-develop"), 27, _("تنزيل صور خام من الموقع الرسمي media/hdd or usb or mmc"), A))
		self.list.append((_("Openspa-7.5"), 28, _("تنزيل صور خام من الموقع الرسمي media/hdd or usb or mmc"), B))
		self.list.append((_("Openspa-8.0"), 29, _("تنزيل صور خام من الموقع الرسمي media/hdd or usb or mmc"), C))
		self.list.append((_("Openspa-8.1"), 30, _("تنزيل صور خام من الموقع الرسمي media/hdd or usb or mmc"), D))
		self.list.append((_("Openspa-8.3"), 31, _("تنزيل صور خام من الموقع الرسمي media/hdd or usb or mmc"), E))
		self.list.append((_("Openspa-8.4"), 32, _("تنزيل صور خام من الموقع الرسمي media/hdd or usb or mmc"), F))
		self.list.append((_("Openvix-6.7"), 33, _("تنزيل صور خام من الموقع الرسمي media/hdd or usb or mmc"), G))
		self.list.append((_("Pure2-6.5"), 34, _("تنزيل صور خام من الموقع الرسمي media/hdd or usb or mmc"), H))
		self.list.append((_("Pure2-7.3"), 35, _("تنزيل صور خام من الموقع الرسمي media/hdd or usb or mmc"), I))
		self.list.append((_("Pure2-7.4"), 36, _("تنزيل صور خام من الموقع الرسمي media/hdd or usb or mmc"), J))
		self.list.append((_("Teamblue-7.5"), 37, _("تنزيل صور خام من الموقع الرسمي media/hdd or usb or mmc"), K))

		if self.indexpos != None:
			self["menu"].setIndex(self.indexpos)
		self["menu"].setList(self.list)
		
	def go(self, num = None):
		if num is not None:
			num -= 1
			if not num < self["menu"].count():
				return
			self["menu"].setIndex(num)
		item = self["menu"].getCurrent()[1]
		self.select_item(item)
		
	def keyOK(self, item = None):
		self.indexpos = self["menu"].getIndex()
		if item == None:
			item = self["menu"].getCurrent()[1]
			self.select_item(item)

	def select_item(self, item):
		if item:
			if item is 1:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/scripts/-/raw/main/images/egami-10.3.sh -qO - | /bin/sh"
        ])
			elif item is 2:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/scripts/-/raw/main/images/egami-10.4.sh -qO - | /bin/sh"
        ])
			elif item is 3:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/scripts/-/raw/main/images/egami-10.5.sh -qO - | /bin/sh"
        ])
			elif item is 4:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/scripts/-/raw/main/images/egami-10.6.sh -qO - | /bin/sh"
        ])
			elif item is 5:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/scripts/-/raw/main/images/openatv-6.4.sh -qO - | /bin/sh"
        ])
			elif item is 6:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/scripts/-/raw/main/images/openatv-7.0.sh -qO - | /bin/sh"
        ])
			elif item is 7:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/scripts/-/raw/main/images/openatv-7.1.sh -qO - | /bin/sh"
        ])
			elif item is 8:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/scripts/-/raw/main/images/openatv-7.2.sh -qO - | /bin/sh"
        ])
			elif item is 9:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/scripts/-/raw/main/images/openatv-7.3.sh -qO - | /bin/sh"
        ])
			elif item is 10:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/scripts/-/raw/main/images/openatv-7.4.sh -qO - | /bin/sh"
        ])
			elif item is 11:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/scripts/-/raw/main/images/openatv-7.5.sh -qO - | /bin/sh"
        ])
			elif item is 12:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/scripts/-/raw/main/images/openatv-7.5.1.sh -qO - | /bin/sh"
        ])
			elif item is 13:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/scripts/-/raw/main/images/openblackhole-4.4.sh -qO - | /bin/sh"
        ])
			elif item is 14:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/scripts/-/raw/main/images/openblackhole-5.0.sh -qO - | /bin/sh"
        ])
			elif item is 15:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/scripts/-/raw/main/images/openblackhole-5.1.sh -qO - | /bin/sh"
        ])
			elif item is 16:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/scripts/-/raw/main/images/openblackhole-5.2.sh -qO - | /bin/sh"
        ])
			elif item is 17:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/scripts/-/raw/main/images/openblackhole-5.3.sh -qO - | /bin/sh"
        ])
			elif item is 18:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/scripts/-/raw/main/images/openblackhole-5.4.sh -qO - | /bin/sh"
        ])
			elif item is 19:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/scripts/-/raw/main/images/opendroid.sh -qO - | /bin/sh"
        ])
			elif item is 20:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/scripts/-/raw/main/images/openhdf-6.5.sh -qO - | /bin/sh"
        ])
			elif item is 21:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/scripts/-/raw/main/images/openhdf-7.2.sh -qO - | /bin/sh"
        ])
			elif item is 22:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/scripts/-/raw/main/images/openhdf-7.3.sh -qO - | /bin/sh"
        ])
			elif item is 23:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/scripts/-/raw/main/images/openpli-7.3.sh -qO - | /bin/sh"
        ])
			elif item is 24:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/scripts/-/raw/main/images/openpli-8.3.sh -qO - | /bin/sh"
        ])
			elif item is 25:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/scripts/-/raw/main/images/openpli-9.0.sh -qO - | /bin/sh"
        ])
			elif item is 26:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/scripts/-/raw/main/images/openpli-9.1.sh -qO - | /bin/sh"
        ])
			elif item is 27:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/scripts/-/raw/main/images/openpli-develop.sh -qO - | /bin/sh"
        ])
			elif item is 28:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/scripts/-/raw/main/images/openspa-7.5.sh -qO - | /bin/sh"
        ])
			elif item is 29:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/scripts/-/raw/main/images/openspa-8.0.sh -qO - | /bin/sh"
        ])
			elif item is 30:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/scripts/-/raw/main/images/openspa-8.1.sh -qO - | /bin/sh"
        ])
			elif item is 31:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/scripts/-/raw/main/images/openspa-8.3.sh -qO - | /bin/sh"
        ])
			elif item is 32:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/scripts/-/raw/main/images/openspa-8.4.sh -qO - | /bin/sh"
        ])
			elif item is 33:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/scripts/-/raw/main/images/openvix.sh -qO - | /bin/sh"
        ])
			elif item is 34:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/scripts/-/raw/main/images/pure2-6.5.sh -qO - | /bin/sh"
        ])
			elif item is 35:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/display/-/raw/main/n-image/bootlogos-n-teamblue.sh -qO - | /bin/sh"
        ])
			elif item is 36:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/scripts/-/raw/main/images/pure2-7.4.sh -qO - | /bin/sh"
        ])
			elif item is 37:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/scripts/-/raw/main/images/teamblue.sh -qO - | /bin/sh"
        ])
			elif item is 38:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/scripts/-/raw/main/images/openblackhole-5.5.1.sh -qO - | /bin/sh"
        ])
			elif item is 39:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/scripts/-/raw/main/images/openatv-7.6.sh -qO - | /bin/sh"
        ])

			else:
				self.close(None)

	def exit(self):
		self.close()

	def keyRed (self):

		self.session.open(PluginBrowser)

	def restart (self):
				self.session.open(Console, _("Restarting enigma2 please wait..."), [
            "[ command -v dpkg &> /dev/null ] && systemctl restart enigma2 || killall -9 enigma2"
        ])

	def keyRed (self):

		self.session.open(PluginBrowser)

	def keyBlue (self):
		self.session.open(PluginBrowser)
				
	def keyYellow (self):
		self.session.open(PluginBrowser)
		
	def keyGreen (self):
		self.session.open(PluginBrowser)
	
	def infoKey (self):
		self.session.open(Console, _("Please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/scripts/-/raw/main/check/_check-all.sh -qO - | /bin/sh"
        ])

	def cancel(self):
		self.close()
