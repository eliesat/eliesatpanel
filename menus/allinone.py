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

class allinone(Screen):
	skin = """
<screen name="allinone" position="0,0" size="1920,1080" backgroundColor="transparent" flags="wfNoBorder" title="ElieSatPanel">
<ePixmap position="0,0" zPosition="-1" size="1920,1080" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ElieSatPanel/images/bglist.png"/>

<!-- title -->
<eLabel text="All in one" position="160,120" size="400,50" zPosition="1" font="Regular;40" halign="left" foregroundColor="white" backgroundColor="#ff2c2d2b" transparent="1" />
<ePixmap position="73,125" size="180,47" zPosition="1" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ElieSatPanel/images/1.png" alphatest="blend" />

<!-- title1 -->
<eLabel text="All in one " position="1500,700" size="400,50" zPosition="1" font="Regular;40" halign="left" foregroundColor="white" backgroundColor="#ff2c2d2b" transparent="1" />

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

		self.list.append((_("Wget"), 1, _("تنزيل و تثبيت باكاج openpli #wget"), a))
		self.list.append((_("Update"), 2, _("تحديث فيدات الصورة"), b))
		self.list.append((_("Upgrade"), 3, _("ترقية الصورة و الباكجات المثبته"), c))
		self.list.append((_("Dependencies"), 4, _("تنزيل و تثبيت المكتبات من فيد الصورة"), d))
		self.list.append((_("Gstreamer"), 5, _("تنزيل و تثبيت باكاج openpli #gstreamer"), e))
		self.list.append((_("Dns-Cloudflare"), 6, _("تأمين سرعة اتصال بالسيرفر و الفيدات"), f))
		self.list.append((_("Dns-Google"), 7, _("تأمين سرعة اتصال بالسيرفر و الفيدات"), g))
		self.list.append((_("Dns-Home opendns"), 8, _("تأمين سرعة اتصال بالسيرفر و الفيدات"), h))
		self.list.append((_("Dns-Opendns"), 9, _("تأمين سرعة اتصال بالسيرفر و الفيدات"), i))
		self.list.append((_("Dns-Quad9"), 10, _("تأمين سرعة اتصال بالسيرفر و الفيدات"), j))
		self.list.append((_("Dns-Default"), 11, _("تثبيت الdns الافتراضي"), k))
		self.list.append((_("Fix-Chmod scripts"), 12, _("اعطاء لايحة السكريبتات تصريح بالتنفيذ"), l))
		self.list.append((_("Fix-Freeserver"), 13, _("حل مشكلة freeserver serviceinfo-module"), m))
		self.list.append((_("Fix-Ipk installation"), 14, _("حل مشكلة تنصيب باكجات بامتداد ipk"), n))
		self.list.append((_("Fix-Inodes"), 15, _("حل مشكلة المساحة no space left"), o))
		self.list.append((_("Fix-Portals to 200"), 16, _("إضافة عدد البورتلات ل ٢٠٠"), p))
		self.list.append((_("Fix-Openpli emu"), 17, _("حل مشكلة اقلاع الايميو صورة openpli"), q))
		self.list.append((_("Fix-Openatv emu"), 18, _("حل مشكلة اقلاع الايميو صورة openatv"), r))
		self.list.append((_("Fix-xtraevent"), 19, _("حل مشكلة اعداد download place"), s))
		self.list.append((_("Fix-xtraevent"), 20, _("حل مشكلة no space left on device"), t))
		self.list.append((_("Hdd-intialize to ext4"), 21, _("فرمطت و تهيئة الذاكرة الخارجية ل ext4"), u))
		self.list.append((_("Hdd-Create swap file"), 22, _("إنشاء ذاكرة تشاركية 1gb"), v))
		self.list.append((_("Remove-Crash logs"), 23, _("حذف ملفات الكراش"), w))
		self.list.append((_("Remove-E2iplayer"), 24, _("حذف بلاجين e2iplayer"), x))
		self.list.append((_("Remove-Emus config folders"), 25, _("حذف مجلدات الconfig الخاص بالايميوهات"), y))
		self.list.append((_("Remove-Emus"), 26, _("حذف الايميوهات"), z))
		self.list.append((_("Remove-Epg rytec sources"), 27, _("حذف سورسات الدليل rytec بلاجين egggrabber"), A))
		self.list.append((_("Remove-Multistalker portals"), 28, _("حذف بورتلات الiptv بلاجين multistalker"), B))
		self.list.append((_("Remove-Picons"), 29, _("حذف البيكونات من جميع المسارات"), C))
		self.list.append((_("Remove-Playlists bouquetmaker"), 30, _("حذف اسطر الiptv و الرجوع للافتراضي"), D))
		self.list.append((_("Remove-Playlists ipaudio"), 31, _("حذف مصادر الصوتيات و الرجوع للافتراضي"), E))
		self.list.append((_("Remove-Playlists iptosat"), 32, _("حذف اسطر الiptv و الرجوع للافتراضي"), F))
		self.list.append((_("Remove-Playlists jedimakerxtream"), 33, _("حذف اسطر الiptv و الرجوع للافتراضي"), G))
		self.list.append((_("Remove-Playlists e2iplayer"), 34, _("حذف اسطر الiptv و الرجوع للافتراضي"), H))
		self.list.append((_("Remove-Playlists xtreamity"), 35, _("حذف اسطر الiptv و الرجوع للافتراضي "), I))
		self.list.append((_("Remove-Channels"), 36, _("ضبط مصنع للاقمار و القنوات"), J))
		self.list.append((_("Remove-Scripts"), 37, _("حذف السكريبتات من المسار الافتراضي"), K))
		self.list.append((_("Remove-Swapper logos"), 38, _("حذف اللوجوهات من بلاجين bootlogoswapper"), L))
		self.list.append((_("Remove-Settings"), 39, _("حذف اعدادات التيونر"), M))

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
            "opkg install wget"
        ])
			elif item is 2:
				self.session.open(Console, _("Installing package please wait..."), [
            "opkg update"
        ])
			elif item is 3:
				self.session.open(Console, _("Installing package please wait..."), [
            "opkg upgrade"
        ])
			elif item is 4:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/scripts/-/raw/main/all/_update-dependencies.sh -qO - | /bin/sh"
        ])
			elif item is 5:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/scripts/-/raw/main/all/_update-dependencies-audio.sh -qO - | /bin/sh"
        ])
			elif item is 6:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/scripts/-/raw/main/all/_dns-cloudflare-installer.sh -qO - | /bin/sh"
        ])
			elif item is 7:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/scripts/-/raw/main/all/_dns-google-installer.sh -qO - | /bin/sh"
        ])
			elif item is 8:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/scripts/-/raw/main/all/_dns-opendns-home-installer.sh -qO - | /bin/sh"
        ])
			elif item is 9:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/scripts/-/raw/main/all/_dns-opendns-installer.sh -qO - | /bin/sh"
        ])
			elif item is 10:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/scripts/-/raw/main/all/_dns-quad9-installer.sh -qO - | /bin/sh"
        ])
			elif item is 11:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/scripts/-/raw/main/remove/_remove-dns.sh -qO - | /bin/sh"
        ])
			elif item is 12:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/scripts/-/raw/main/all/_chmod-scripts.sh -qO - | /bin/sh"
        ])
			elif item is 13:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/scripts/-/raw/main/all/_fix-freeserver-serviceinfo-module.sh -qO - | /bin/sh"
        ])
			elif item is 14:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/scripts/-/raw/main/all/_fix-ipk-package-installation.sh -qO - | /bin/sh"
        ])
			elif item is 15:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/scripts/-/raw/main/all/_fix-hdd--space-inodes.sh -qO - | /bin/sh"
        ])
			elif item is 16:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/scripts/-/raw/main/all/_fix-portals-to200.sh -qO - | /bin/sh"
        ])
			elif item is 17:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/softcams/-/raw/main/support/support-2-r0.2.sh -qO - | /bin/sh"
        ])
			elif item is 18:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/scripts/-/raw/main/all/_fix-atv-softcam-restart.sh -qO - | /bin/sh"
        ])
			elif item is 19:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/scripts/-/raw/main/all/_fix-xtraevent-download-place.sh -qO - | /bin/sh"
        ])
			elif item is 20:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/scripts/-/raw/main/all/_fix-xtraevent-nospace.sh -qO - | /bin/sh"
        ])
			elif item is 21:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/scripts/-/raw/main/all/_hdd-intialize-ext4.sh -qO - | /bin/sh"
        ])
			elif item is 22:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/scripts/-/raw/main/all/_hdd-create-swapfile-1gb.sh -qO - | /bin/sh"
        ])
			elif item is 23:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/scripts/-/raw/main/remove/_remove-crash-logs.sh -qO - | /bin/sh"
        ])
			elif item is 24:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/scripts/-/raw/main/remove/_remove-e2iplayer.sh -qO - | /bin/sh"
        ])
			elif item is 25:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/scripts/-/raw/main/remove/_remove-emus-config-files.sh -qO - | /bin/sh"
        ])
			elif item is 26:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/scripts/-/raw/main/remove/_remove-emus.sh -qO - | /bin/sh"
        ])
			elif item is 27:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/scripts/-/raw/main/remove/_remove-epg-rytec-sources.sh -qO - | /bin/sh"
        ])
			elif item is 28:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/scripts/-/raw/main/remove/_remove-multistalker-portals.sh -qO - | /bin/sh"
        ])
			elif item is 29:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/scripts/-/raw/main/remove/_remove-picons.sh -qO - | /bin/sh"
        ])
			elif item is 30:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/scripts/-/raw/main/remove/_remove-playlists-bouquetmakerxtream.sh -qO - | /bin/sh"
        ])
			elif item is 31:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/scripts/-/raw/main/remove/_remove-playlists-ipaudio.sh -qO - | /bin/sh"
        ])
			elif item is 32:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/scripts/-/raw/main/remove/_remove-playlists-iptosat.sh -qO - | /bin/sh"
        ])
			elif item is 33:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/scripts/-/raw/main/remove/_remove-playlists-jedimakerxtream.sh -qO - | /bin/sh"
        ])
			elif item is 34:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/scripts/-/raw/main/remove/_remove-playlists-tsiplayer.sh -qO - | /bin/sh"
        ])
			elif item is 35:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/scripts/-/raw/main/remove/_remove-playlists-xstreamity.sh -qO - | /bin/sh"
        ])
			elif item is 36:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/scripts/-/raw/main/remove/_remove-sats-channels-lists.sh -qO - | /bin/sh"
        ])
			elif item is 37:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/scripts/-/raw/main/remove/_remove-scripts.sh -qO - | /bin/sh"
        ])
			elif item is 38:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/scripts/-/raw/main/remove/_remove-bootlogo-swapper-logos.sh -qO - | /bin/sh"
        ])
			elif item is 39:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/scripts/-/raw/main/all/_fix-xtraevent-download-place.sh -qO - | /bin/sh"
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
