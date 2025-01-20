
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

class extensions(Screen):
	skin = """
<screen name="extensions" position="0,0" size="1920,1080" backgroundColor="transparent" flags="wfNoBorder" title="ElieSatPanel">
<ePixmap position="0,0" zPosition="-1" size="1920,1080" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ElieSatPanel/images/bglist.png"/>

<!-- title -->
<eLabel text="Extensions" position="160,120" size="400,50" zPosition="1" font="Regular;40" halign="left" foregroundColor="white" backgroundColor="#ff2c2d2b" transparent="1" />
<ePixmap position="55,125" size="180,47" zPosition="1" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ElieSatPanel/images/1.png" alphatest="blend" />

<!-- title1 -->
<eLabel text="Extensions" position="1490,700" size="400,50" zPosition="1" font="Regular;40" halign="left" foregroundColor="white" backgroundColor="#ff2c2d2b" transparent="1" />

<!-- title2 -->
<eLabel text="Select and press ok to install" position="1440,790" size="400,50" zPosition="1" font="Bold;27" halign="left" foregroundColor="white" backgroundColor="#ff2c2d2b" transparent="1" />

<!-- minitv -->
<widget source="session.VideoPicture" render="Pig" position="1320,120" size="550,400" zPosition="1" backgroundColor="#ff000000" />

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
<widget source="menu" selectionPixmap="/usr/lib/enigma2/python/Plugins/Extensions/ElieSatPanel/images/selection.png" render="Listbox" position="48,200" size="1240,660" scrollbarMode="showOnDemand">
<convert type="TemplatedMultiContent">
	{"template": [
		MultiContentEntryText(pos = (120, 10), size = (600, 45), font=0, flags = RT_HALIGN_LEFT, text = 0), # index 2 is the Menu Titel
		MultiContentEntryText(pos = (700, 19), size = (600, 35), font=1, flags = RT_HALIGN_LEFT, text = 2), # index 3 is the Description
		MultiContentEntryPixmapAlphaTest(pos = (6, 10), size = (100, 40), png = 3), # index 4 is the pixmap
			],
	"fonts": [gFont("Regular", 35),gFont("Regular", 25)],
	"itemHeight": 64
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
		P = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/images/1.png"))
		Q = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/images/1.png"))
		R = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/images/1.png"))
		S = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/images/1.png"))
		T = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/images/1.png"))
		U = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/images/1.png"))
		V = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/images/1.png"))
		W = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/images/1.png"))
		X = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/images/1.png"))
		Y = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/images/1.png"))
		Z = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/images/1.png"))

		self.list.append((_("Acherone-1.2"), 1, _("تصفح لايحة السكريبتات و تنفيذهم"), a))
		self.list.append((_("Alajre-1.2"), 2, _("الأجر py2"), b))
		self.list.append((_("Alternativesoftcammanager-2.0"), 3, _("ادارة الكامات"), c))
		self.list.append((_("Apod-1.4"), 4, _("صورة و معلومات عن كوكب الارض"), d))
		self.list.append((_("Ansite-1.6"), 5, _("انصت للقرآن الكريم"), e))
		self.list.append((_("Arabic-savior-2.1"), 6, _("اصلاح اللغة العربية"), f))
		self.list.append((_("Astronomy-1.3"), 7, _("الفلك و حركة الكواكب مباشرة اون لاين"), g))
		self.list.append((_("Athantimes-2.8"), 8, _("الآذان"), h))
		self.list.append((_("Azkar-1.0"), 9, _("اذكار المسلم mod elsafty"), i))
		self.list.append((_("Azkar-almuslim-1.1"), 10, _("اذكار المسلم"), j))
		self.list.append((_("xxxx"), 11, _("xxxx"), k))
		self.list.append((_("xxxx"), 12, _("xxxx"), l))
		self.list.append((_("xxxx"), 13, _("xxxx"), m))
		self.list.append((_("xxxx"), 14, _("xxxx"), n))
		self.list.append((_("xxxx"), 15, _("xxxx"), o))
		self.list.append((_("xxxx"), 16, _("xxxx"), p))
		self.list.append((_("xxxx"), 17, _("xxxx"), q))
		self.list.append((_("xxxx"), 18, _("xxxx"), r))
		self.list.append((_("xxxx"), 19, _("xxxx"), s))
		self.list.append((_("xxxx"), 20, _("xxxx"), t))
		self.list.append((_("xxxx"), 21, _("xxxx"), u))
		self.list.append((_("xxxx"), 22, _("xxxx"), v))
		self.list.append((_("xxxx"), 23, _("xxxx"), w))
		self.list.append((_("xxxx"), 24, _("xxxx"), x))
		self.list.append((_("xxxx"), 25, _("xxxx"), y))
		self.list.append((_("xxxx"), 26, _("xxxx"), z))
		self.list.append((_("xxxx"), 27, _("xxxx"), A))
		self.list.append((_("xxxx"), 28, _("xxxx"), B))
		self.list.append((_("xxxx"), 29, _("xxxx"), C))
		self.list.append((_("xxxx"), 30, _("xxxx"), D))
		self.list.append((_("xxxx"), 31, _("xxxz"), E))
		self.list.append((_("xxxx"), 32, _("xxxx"), F))
		self.list.append((_("xxxx"), 33, _("xxxx"), G))
		self.list.append((_("xxxx"), 34, _("xxxx"), H))
		self.list.append((_("xxxx"), 35, _("xxxx"), I))
		self.list.append((_("xxxx"), 36, _("xxxx"), J))
		self.list.append((_("xxxx"), 37, _("xxxx"), K))
		self.list.append((_("xxxx"), 38, _("xxxx"), L))
		self.list.append((_("xxxx"), 39, _("xxxx"), M))
		self.list.append((_("xxxx"), 40, _("xxxx"), N))
		self.list.append((_("xxxx"), 41, _("xxxx"), O))
		self.list.append((_("xxxx"), 42, _("xxxz"), P))
		self.list.append((_("xxxx"), 43, _("xxxx"), Q))
		self.list.append((_("xxxx"), 44, _("xxxx"), R))
		self.list.append((_("xxxx"), 45, _("xxxx"), S))
		self.list.append((_("xxxx"), 46, _("xxxx"), T))
		self.list.append((_("xxxx"), 47, _("xxxx"), U))
		self.list.append((_("xxxx"), 48, _("xxxx"), V))
		self.list.append((_("xxxx"), 49, _("xxxx"), W))
		self.list.append((_("xxxx"), 50, _("xxxx"), X))
		self.list.append((_("xxxx"), 51, _("xxxx"), Y))
		self.list.append((_("xxxx"), 52, _("xxxx"), Z))

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
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/acherone/acherone.sh -qO - | /bin/sh"
        ])
			elif item is 2:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/alajre/alajre.sh -qO - | /bin/sh"
        ])
			elif item is 3:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/alternativesoftcammanager/alternativesoftcammanager.sh -qO - | /bin/sh"
        ])
			elif item is 4:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/apod/apod.sh -qO - | /bin/sh"
        ])
			elif item is 5:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/ansite/ansite.sh -qO - | /bin/sh"
        ])
			elif item is 6:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/arabicsavior/arabicsavior.sh -qO - | /bin/sh"
        ])
			elif item is 7:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/astronomy/astronomy.sh -qO - | /bin/sh"
        ])
			elif item is 8:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/athantimes/athantimes.sh -qO - | /bin/sh"
        ])
			elif item is 9:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/athkar/athkar.sh -qO - | /bin/sh"
        ])
			elif item is 10:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/azkar-almuslim/azkar-almuslim.sh -qO - | /bin/sh"
        ])
			elif item is 11:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/weathercomponenthandler/weathercomponenthandler.sh -qO - | /bin/sh"
        ])
			elif item is 12:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/systemplugins/-/raw/main/xmlupdate/xmlupdate.sh -qO - | /bin/sh"
        ])
			elif item is 13:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/display/-/raw/main/vu+/bootlogos-vu+.sh -qO - | /bin/sh"
        ])
			elif item is 14:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/display/-/raw/main/n-image/bootlogos-n-areadelta.sh -qO - | /bin/sh"
        ])
			elif item is 15:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/display/-/raw/main/n-image/bootlogos-n-cobralibero.sh -qO - | /bin/sh"
        ])
			elif item is 16:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/display/-/raw/main/n-image/bootlogos-n-egami.sh -qO - | /bin/sh"
        ])
			elif item is 17:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/display/-/raw/main/n-image/bootlogos-n-nonsolosat.sh -qO - | /bin/sh"
        ])
			elif item is 18:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/display/-/raw/main/n-image/bootlogos-n-novaler.sh -qO - | /bin/sh"
        ])
			elif item is 19:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/display/-/raw/main/n-image/bootlogos-n-openatv.sh -qO - | /bin/sh"
        ])
			elif item is 20:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/display/-/raw/main/n-image/bootlogos-n-openblackhole.sh -qO - | /bin/sh"
        ])
			elif item is 21:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/display/-/raw/main/n-image/bootlogos-n-opendroid.sh -qO - | /bin/sh"
        ])
			elif item is 22:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/display/-/raw/main/n-image/bootlogos-n-openeight.sh -qO - | /bin/sh"
        ])
			elif item is 23:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/display/-/raw/main/n-image/bootlogos-n-openfix.sh -qO - | /bin/sh"
        ])
			elif item is 24:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/display/-/raw/main/n-image/bootlogos-n-openhdf.sh -qO - | /bin/sh"
        ])
			elif item is 25:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/display/-/raw/main/n-image/bootlogos-n-opennfr.sh -qO - | /bin/sh"
        ])
			elif item is 26:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/display/-/raw/main/n-image/bootlogos-n-openpli.sh -qO - | /bin/sh"
        ])
			elif item is 27:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/display/-/raw/main/n-image/bootlogos-n-openspa.sh -qO - | /bin/sh"
        ])
			elif item is 28:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/display/-/raw/main/n-image/bootlogos-n-opentr.sh -qO - | /bin/sh"
        ])
			elif item is 29:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/display/-/raw/main/n-image/bootlogos-n-openvision.sh -qO - | /bin/sh"
        ])
			elif item is 30:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/display/-/raw/main/n-image/bootlogos-n-openvix.sh -qO - | /bin/sh"
        ])
			elif item is 31:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/display/-/raw/main/n-image/bootlogos-n-pkteam.sh -qO - | /bin/sh"
        ])
			elif item is 32:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/display/-/raw/main/n-image/bootlogos-n-pure2.sh -qO - | /bin/sh"
        ])
			elif item is 33:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/display/-/raw/main/n-image/bootlogos-n-satdreamgr.sh -qO - | /bin/sh"
        ])
			elif item is 34:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/display/-/raw/main/n-image/bootlogos-n-satlodge.sh -qO - | /bin/sh"
        ])
			elif item is 35:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/display/-/raw/main/n-image/bootlogos-n-teamblue.sh -qO - | /bin/sh"
        ])
			elif item is 36:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/display/-/raw/main/bootvideo1/openatv.sh -qO - | /bin/sh"
        ])
			elif item is 37:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/display/-/raw/main/bootvideo1/openatv.sh -qO - | /bin/sh"
        ])
			elif item is 38:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/alajre/alajre.sh -qO - | /bin/sh"
        ])
			elif item is 39:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/alternativesoftcammanager/alternativesoftcammanager.sh -qO - | /bin/sh"
        ])
			elif item is 40:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/apod/apod.sh -qO - | /bin/sh"
        ])
			elif item is 41:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/ansite/ansite.sh -qO - | /bin/sh"
        ])
			elif item is 42:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/arabicsavior/arabicsavior.sh -qO - | /bin/sh"
        ])
			elif item is 43:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/astronomy/astronomy.sh -qO - | /bin/sh"
        ])
			elif item is 44:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/athantimes/athantimes.sh -qO - | /bin/sh"
        ])
			elif item is 45:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/athkar/athkar.sh -qO - | /bin/sh"
        ])
			elif item is 46:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/azkar-almuslim/azkar-almuslim.sh -qO - | /bin/sh"
        ])
			elif item is 47:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/weathercomponenthandler/weathercomponenthandler.sh -qO - | /bin/sh"
        ])
			elif item is 48:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/systemplugins/-/raw/main/xmlupdate/xmlupdate.sh -qO - | /bin/sh"
        ])
			elif item is 49:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/display/-/raw/main/vu+/bootlogos-vu+.sh -qO - | /bin/sh"
        ])
			elif item is 50:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/display/-/raw/main/n-image/bootlogos-n-areadelta.sh -qO - | /bin/sh"
        ])
			elif item is 51:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/display/-/raw/main/n-image/bootlogos-n-areadelta.sh -qO - | /bin/sh"
        ])
			elif item is 52:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/display/-/raw/main/n-image/bootlogos-n-areadelta.sh -qO - | /bin/sh"
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
