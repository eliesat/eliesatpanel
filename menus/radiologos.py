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

class radiologos(Screen):
	skin = """
<screen name="radiologos" position="0,0" size="1920,1080" backgroundColor="transparent" flags="wfNoBorder" title="ElieSatPanel">
<ePixmap position="0,0" zPosition="-1" size="1920,1080" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ElieSatPanel/images/bglist.png"/>

<!-- title -->
<eLabel text="Radiologos" position="160,120" size="400,50" zPosition="1" font="Regular;40" halign="left" foregroundColor="white" backgroundColor="#ff2c2d2b" transparent="1" />
<ePixmap position="73,125" size="180,47" zPosition="1" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ElieSatPanel/images/1.png" alphatest="blend" />

<!-- title1 -->
<eLabel text="Radiologos" position="1500,700" size="400,50" zPosition="1" font="Regular;40" halign="left" foregroundColor="white" backgroundColor="#ff2c2d2b" transparent="1" />

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
		MultiContentEntryText(pos = (700, 19), size = (600, 35), font=1, flags = RT_HALIGN_LEFT, text = 2), # index 3 is the Description
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

		self.list.append((_("Radiologo1"), 1, _("تغيير خلفية قنوات الراديو"), a))
		self.list.append((_("Radiologo2"), 2, _("تغيير خلفية قنوات الراديو"), b))
		self.list.append((_("Radiologo3"), 3, _("تغيير خلفية قنوات الراديو"), c))
		self.list.append((_("Radiologo4"), 4, _("تغيير خلفية قنوات الراديو"), d))
		self.list.append((_("Radiologo5"), 5, _("تغيير خلفية قنوات الراديو"), e))
		self.list.append((_("Radiologo6"), 6, _("تغيير خلفية قنوات الراديو"), f))
		self.list.append((_("Radiologo7"), 7, _("تغيير خلفية قنوات الراديو"), g))
		self.list.append((_("Radiologo8"), 8, _("تغيير خلفية قنوات الراديو"), h))
		self.list.append((_("Radiologo9"), 9, _("تغيير خلفية قنوات الراديو"), i))
		self.list.append((_("Radiologo10"), 10, _("تغيير خلفية قنوات الراديو"), j))
		self.list.append((_("Radiologo11"), 11, _("تغيير خلفية قنوات الراديو"), k))
		self.list.append((_("Radiologo12"), 12, _("تغيير خلفية قنوات الراديو"), l))

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
            "wget --no-check-certificate https://gitlab.com/eliesat/display/-/raw/main/radiologo/radiologo-1.sh -qO - | /bin/sh"
        ])
			elif item is 2:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/display/-/raw/main/radiologo/radiologo-2.sh -qO - | /bin/sh"
        ])
			elif item is 3:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/display/-/raw/main/radiologo/radiologo-3.sh -qO - | /bin/sh"
        ])
			elif item is 4:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/display/-/raw/main/radiologo/radiologo-4.sh -qO - | /bin/sh"
        ])
			elif item is 5:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/display/-/raw/main/radiologo/radiologo-.sh -qO - | /bin/sh"
        ])
			elif item is 6:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/display/-/raw/main/radiologo/radiologo-6.sh -qO - | /bin/sh"
        ])
			elif item is 7:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/display/-/raw/main/radiologo/radiologo-7.sh -qO - | /bin/sh"
        ])
			elif item is 8:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/display/-/raw/main/radiologo/radiologo-8.sh -qO - | /bin/sh"
        ])
			elif item is 9:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/display/-/raw/main/radiologo/radiologo-9.sh -qO - | /bin/sh"
        ])
			elif item is 10:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/display/-/raw/main/radiologo/radiologo-10.sh -qO - | /bin/sh"
        ])
			elif item is 11:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/display/-/raw/main/radiologo/radiologo-11.sh -qO - | /bin/sh"
        ])
			elif item is 12:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/display/-/raw/main/radiologo/radiologo-12.sh -qO - | /bin/sh"
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
