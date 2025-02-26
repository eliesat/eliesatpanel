#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import _enigma
import enigma
import socket
import gzip
import stat
import sys, traceback
import re
import time
import gettext
from datetime import datetime
from threading import Timer
from .menus.compat import compat_urlopen, compat_Request, PY3
from Plugins.Extensions.ElieSatPanel.menus.Console import Console
from Plugins.Extensions.ElieSatPanel.menus.allinone import allinone
from Plugins.Extensions.ElieSatPanel.menus.dependencies import dependencies
from Plugins.Extensions.ElieSatPanel.menus.display import display
from Plugins.Extensions.ElieSatPanel.menus.drivers import drivers
from Plugins.Extensions.ElieSatPanel.menus.extensions import extensions
from Plugins.Extensions.ElieSatPanel.menus.feeds import feeds
from Plugins.Extensions.ElieSatPanel.menus.free import free
from Plugins.Extensions.ElieSatPanel.menus.imagesd import imagesd
from Plugins.Extensions.ElieSatPanel.menus.imagesb import imagesb
from Plugins.Extensions.ElieSatPanel.menus.lcdskins import lcdskins
from Plugins.Extensions.ElieSatPanel.menus.multiboot import multiboot
from Plugins.Extensions.ElieSatPanel.menus.novaler import novaler
from Plugins.Extensions.ElieSatPanel.menus.panels import panels
from Plugins.Extensions.ElieSatPanel.menus.picons import picons
from Plugins.Extensions.ElieSatPanel.menus.radiologos import radiologos
from Plugins.Extensions.ElieSatPanel.menus.settings import settings
from Plugins.Extensions.ElieSatPanel.menus.skins import skins
from Plugins.Extensions.ElieSatPanel.menus.softcams import softcams
from Plugins.Extensions.ElieSatPanel.menus.spinners import spinners
from Plugins.Extensions.ElieSatPanel.menus.systemplugins import systemplugins
from Components.ConfigList import ConfigListScreen
from Components.config import ConfigText, getConfigListEntry
from Components.PluginComponent import plugins
from Components.Sources.StaticText import StaticText
from Components.Pixmap import Pixmap
from Components.ActionMap import ActionMap, NumberActionMap
from Components.Sources.List import List
from Components.Label import Label
from Components.MenuList import MenuList
from Components.Button import Button
from Components.Harddisk import harddiskmanager
from enigma import *
from os import environ
from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Screens.PluginBrowser import PluginBrowser
from Screens.Standby import TryQuitMainloop
from Screens.MessageBox import MessageBox
from Tools.LoadPixmap import LoadPixmap
from Components.Console import Console as iConsole
from Tools.Directories import fileExists, pathExists, resolveFilename, SCOPE_PLUGINS, SCOPE_LANGUAGE
from types import *

global min, first_start
min = first_start = 0
Panel = 'ElieSatPanel'
Version = '2.60'
installer = 'https://raw.githubusercontent.com/eliesat/eliesatpanel/main/installer.sh'
scriptpath = "/usr/script/"

class eliesatpanel(Screen):
	skin = """
<screen name="eliesatpanel" position="0,0" size="1920,1080" backgroundColor="transparent" flags="wfNoBorder" title="ElieSatPanel">
<ePixmap position="0,0" zPosition="-1" size="1920,1080" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ElieSatPanel/images/bglist.png"/>

<!-- title -->
<widget name="Panel" position="160,105" size="270,50" font="Regular;45" halign="center" valign="center" backgroundColor="background" foregroundColor="foreground" transparent="1"/>
<widget name="Version" position="410,110" size="150,50" font="Regular;35" halign="center" valign="center" backgroundColor="background" foregroundColor="foreground" transparent="1"/>
<ePixmap position="73,105" size="180,47" zPosition="1" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ElieSatPanel/images/2.png" alphatest="blend" />

<!-- hdd -->
<widget source="device" render="Label" position="160,895" zPosition="2" size="1000,45" font="Regular;35" halign="left" valign="top" backgroundColor="background" foregroundColor="foreground" transparent="1" />
<ePixmap position="70,890" size="180,47" zPosition="1" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ElieSatPanel/images/2.png" alphatest="blend" />

<!-- ip address -->
<widget source="ipLabel" render="Label" position="1350,895" zPosition="2" size="180,40" font="Regular;35" halign="right" valign="center" backgroundColor="background" foregroundColor="foreground" transparent="1" />
	<widget source="ipInfo" render="Label" position="1540,895" zPosition="2" size="390,40" font="Regular;35" halign="left" valign="center" backgroundColor="background" foregroundColor="foreground" transparent="1" />
<ePixmap position="1280,890" size="180,47" zPosition="1" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ElieSatPanel/images/2.png" alphatest="blend" />

<!-- minitv -->
<widget source="session.VideoPicture" render="Pig" position="1305,100" size="550,290" zPosition="1" backgroundColor="#ff000000" />

<!-- clock -->
<widget source="global.CurrentTime" render="Label" position="650,85" size="350,90" font="lsat; 60" noWrap="1" halign="center" valign="bottom" backgroundColor="background" foregroundColor="foreground" transparent="1" zPosition="2">
		<convert type="ClockToText">Default</convert>

<!-- calender -->
</widget>
<widget source="global.CurrentTime" render="Label" position="880,100" size="335,54" font="lsat; 24" halign="center" valign="bottom" backgroundColor="background" foregroundColor="foreground" transparent="1" zPosition="1">
<convert type="ClockToText">Format %A %d %B</convert>
</widget>

<!-- button -->
<ePixmap position="120,1015" zPosition="1" size="240,10" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ElieSatPanel/images/red.png" alphatest="blend" />
<widget source="key_red" render="Label" position="115,960" zPosition="2" size="265,45" font="Regular;35" halign="center" valign="center" backgroundColor="background" foregroundColor="foreground" transparent="1" />
<ePixmap position="400,1015" zPosition="1" size="240,10" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ElieSatPanel/images/green.png" alphatest="blend" />
<widget source="key_green" render="Label" position="387.5,960" zPosition="2" size="265,45" font="Regular;35" halign="center" valign="center" backgroundColor="background" foregroundColor="foreground" transparent="1" />
<ePixmap position="680,1015" zPosition="1" size="240,10" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ElieSatPanel/images/yellow.png" alphatest="blend" />
<widget source="key_yellow" render="Label" position="720,960" zPosition="2" size="165,45" font="Regular;35" halign="center" valign="center" backgroundColor="background" foregroundColor="foreground" transparent="1" />
<ePixmap position="960,1015" zPosition="1" size="240,10" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ElieSatPanel/images/blue.png" alphatest="blend" />
<widget source="key_blue" render="Label" position="1000,960" zPosition="2" size="165,45" font="Regular;35" halign="center" valign="center" backgroundColor="background" foregroundColor="foreground" transparent="1" />

<!-- menu list -->
<widget source="menu" selectionPixmap="/usr/lib/enigma2/python/Plugins/Extensions/ElieSatPanel/images/selection.png" render="Listbox" position="48,200" size="1240,660" scrollbarMode="showOnDemand" transparent="1">
<convert type="TemplatedMultiContent">
	{"template": [
		MultiContentEntryText(pos = (120, 10), size = (600, 45), font=0, flags = RT_HALIGN_LEFT, text = 0), # menu title
		MultiContentEntryText(pos = (600, 19), size = (600, 35), font=1, flags = RT_HALIGN_LEFT, text = 2), # description
		MultiContentEntryPixmapAlphaTest(pos = (25, 5), size = (50, 40), png = 3), # picture
			],
	"fonts": [gFont("Regular", 35),gFont("Regular", 25)],
	"itemHeight": 66
	}
	</convert>

<!-- info button -->
</widget>
<ePixmap position="1700,800" size="140,60" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ElieSatPanel/images/info.png" zPosition="2" alphatest="blend" />

<!-- image -->
<widget source="ImageLabel" render="Label" position="1280,536.5" zPosition="2" size="180,40" font="lsat; 24" halign="right" valign="center" backgroundColor="background" foregroundColor="#aaaaaa" transparent="1" />
<widget source="Image" render="Label" position="1470,540" zPosition="2" size="390,40" font="lsat; 24" halign="left" valign="center" backgroundColor="background" foregroundColor="foreground" transparent="1" />

<!-- python -->
<widget source="pythonLabel" render="Label" position="1280,570.5" zPosition="2" size="180,40" font="lsat; 24" halign="right" valign="center" backgroundColor="background" foregroundColor="#aaaaaa" transparent="1" />
<widget source="python" render="Label" position="1470,570" zPosition="2" size="390,40" font="lsat; 24" halign="left" valign="center" backgroundColor="background" foregroundColor="foreground" transparent="1" />

<!-- last upgrade -->
<widget source="EnigmaVersionLabel" render="Label" position="1280,600.5" zPosition="2" size="180,40" font="lsat; 24" halign="right" valign="center" backgroundColor="background" foregroundColor="#aaaaaa" transparent="1" />
<widget source="EnigmaVersion" render="Label" position="1470,600" zPosition="2" size="390,40" font="lsat; 24" halign="left" valign="center" backgroundColor="background" foregroundColor="foreground" transparent="1" />
	
<!-- hardware -->
<widget source="HardwareLabel" render="Label" position="1280,660.5" zPosition="2" size="180,40" font="lsat; 24" halign="right" valign="center" backgroundColor="background" foregroundColor="#aaaaaa" transparent="1" />
<widget source="Hardware" render="Label" position="1470,660" zPosition="2" size="390,40" font="lsat; 24" halign="left" valign="center" backgroundColor="background" foregroundColor="foreground" transparent="1" />

<!-- processor -->
<widget source="CPULabel" render="Label" position="1280,690.5" zPosition="2" size="180,50" font="lsat; 24" halign="right" valign="center" backgroundColor="background" foregroundColor="#aaaaaa" transparent="1" />
<widget source="CPU" render="Label" position="1470,690" zPosition="2" size="400,50" font="lsat; 22" halign="left" valign="center" backgroundColor="background" foregroundColor="foreground" transparent="1" />

<!-- mac address -->
<widget source="macLabel" render="Label" position="1300,2770.5" zPosition="2" size="180,50" font="lsat; 24" halign="right" valign="center" backgroundColor="background" foregroundColor="#aaaaaa" transparent="1"/>
<widget source="macInfo" render="Label" position="1490,2770" zPosition="2" size="200,50" font="lsat; 24" halign="left" valign="center" backgroundColor="background" foregroundColor="foreground" transparent="1" />

<!-- driver version-->
<widget source="driverLabel" render="Label" position="1280,750.5" zPosition="2" size="180,40" font="lsat; 24" halign="right" valign="center" backgroundColor="background" foregroundColor="#aaaaaa" transparent="1" />
<widget source="driver" render="Label" position="1470,755" zPosition="2" size="390,30" font="lsat; 24" halign="left" valign="center" backgroundColor="background" foregroundColor="foreground" transparent="1" />

<!-- kernel version -->
<widget source="KernelLabel" render="Label" position="1280,780.5" zPosition="2" size="180,40" font="lsat; 24" halign="right" valign="center" backgroundColor="background" foregroundColor="#aaaaaa" transparent="1" />
<widget source="Kernel" render="Label" position="1470,780" zPosition="2" size="390,40" font="lsat; 24" halign="left" valign="center" backgroundColor="background" foregroundColor="foreground" transparent="1" />

<!-- gstreamer -->
<widget source="gstreamerLabel" render="Label" position="1280,810.5" zPosition="2" size="180,40" font="lsat; 24" halign="right" valign="center" backgroundColor="background" foregroundColor="#aaaaaa" transparent="1" />
<widget source="gstreamer" render="Label" position="1470,810" zPosition="2" size="390,40" font="lsat; 24" halign="left" valign="center" backgroundColor="background" foregroundColor="foreground" transparent="1" />

<!-- ram -->
<widget source="MemoryLabel" render="Label" position="1230,415" zPosition="2" size="150,40" font="lsat; 24" halign="right" backgroundColor="background" foregroundColor="#aaaaaa" transparent="1" />
<widget source="memTotal" render="Label" position="1390,410" zPosition="2" size="420,40" font="lsat; 24" halign="left" valign="center" backgroundColor="background" foregroundColor="foreground" transparent="1" />

<!-- swap -->
<widget source="SwapLabel" render="Label" position="1230,450" zPosition="2" size="150,40" font="lsat; 24" halign="right" backgroundColor="background" foregroundColor="#aaaaaa" transparent="1" />
<widget source="swapTotal" render="Label" position="1390,445" zPosition="2" size="420,40" font="lsat; 24" halign="left" valign="center" backgroundColor="background" foregroundColor="foreground" transparent="1" />

<!-- flash -->
<widget source="FlashLabel" render="Label" position="1200,485" zPosition="2" size="180,40" font="lsat; 24" halign="right" valign="center" backgroundColor="background" foregroundColor="#aaaaaa" transparent="1" />
<widget source="flashTotal" render="Label" position="1390,485" zPosition="2" size="620,40" font="lsat; 23" halign="left" valign="center" backgroundColor="background" foregroundColor="foreground" transparent="1" />

<!-- internet -->
	<widget source="internet" render="Label" position="1505,950" zPosition="2" size="390,40" font="Regular;35" halign="left" valign="center" backgroundColor="background" foregroundColor="foreground" transparent="1" />
<widget source="internetLabel" render="Label" position="1315,950" zPosition="2" size="180,40" font="Regular;35" halign="right" valign="center" backgroundColor="background" foregroundColor="foreground" transparent="1" />
<ePixmap position="1280,945" size="180,47" zPosition="1" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ElieSatPanel/images/2.png" alphatest="blend" />

</screen>"""

	def __init__(self, session):
		self.session = session
		Screen.__init__(self, session)
		self.setTitle(_("ElieSatPanel"))
		self.iConsole = iConsole()
		self.indexpos = None
		self["NumberActions"] = NumberActionMap(["NumberActions"], {'0': self.keyNumberGlobal,
                                                                    },)
		self["shortcuts"] = NumberActionMap(["ShortcutActions", "WizardActions",  "ColorActions", "HotkeyActions"],
		{
			"ok": self.keyOK,
			"cancel": self.exit,
			"back": self.exit,
			"red": self.iptv,
			"info": self.infoKey,
			"green": self.cccam,
			"yellow": self.grid,
			"blue": self.scriptslist,
		})
		self["key_red"] = StaticText(_("IptvAdder"))
		self["key_green"] = StaticText(_("CccamAdder"))
		self["key_yellow"] = StaticText(_("GridMode"))
		self["key_blue"] = StaticText(_("Scripts"))
		self.list = []
		self["menu"] = List(self.list)
		self.mList()
		self["MemoryLabel"] = StaticText(_("Ram:"))
		self["SwapLabel"] = StaticText(_("Swap:"))
		self["FlashLabel"] = StaticText(_("Flash:"))
		self["memTotal"] = StaticText()
		self["swapTotal"] = StaticText()
		self["flashTotal"] = StaticText()
		self["device"] = StaticText()
		self["gstreamerLabel"] = StaticText(_("GStreamer:"))
		self["pythonLabel"] = StaticText(_("Python:"))
		self["gstreamer"] = StaticText()
		self["python"] = StaticText()
		self["Hardware"] = StaticText()
		self["Image"] = StaticText()
		self["CPULabel"] = StaticText(_("Processor:"))
		self["CPU"] = StaticText()
		self["Kernel"] = StaticText()
		self["ipLabel"] = StaticText(_("IP address:"))
		self["ipInfo"] = StaticText()
		self["macLabel"] = StaticText(_("Mac Address:"))
		self["macInfo"] = StaticText()
		self["EnigmaVersion"] = StaticText()
		self["HardwareLabel"] = StaticText(_("Hardware:"))
		self["ImageLabel"] = StaticText(_("Image:"))
		self["KernelLabel"] = StaticText(_("Kernel Ver:"))
		self["EnigmaVersionLabel"] = StaticText(_("Last Upgrade:"))
		self["driver"] = StaticText()
		self["driverLabel"] = StaticText(_("Driver Ver:"))
		self.memInfo()
		self.FlashMem()
		self.devices()
		self.mainInfo()
		self.cpuinfo()
		self.getPythonVersionString()
		self.getGStreamerVersionString()
		self.network_info()
		self["Version"] = Label(_("V" + Version))
		self["Panel"] = Label(_(Panel))
		self["internetLabel"] = StaticText(_("Internet:"))
		self["internet"] = StaticText()
		self.intInfo()
		t = Timer(0.5, self.update_me)
		t.start()

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
		

		self.list.append((_("Allinone"), 1, _("خدمات و اكواد لينوكس"), a))
		self.list.append((_("Dependencies"), 2, _("مكتبات و ادوات تشغيل"), b))
		self.list.append((_("Display"), 3, _("صور و فيديوهات اقلاع"), c))
		self.list.append((_("Drivers"), 4, _("تعريفات"), d))
		self.list.append((_("Extensions"), 5, _("بلاجينات و اضافات الانيجما٢"), e))
		self.list.append((_("Feeds"), 6, _("فيدات منوعة"), f))
		self.list.append((_("Free"), 7, _("اضافات مجانية"), g))
		self.list.append((_("Images (download)"), 8, _("تنزيل صور خام من الموقع الرسمي"), h))
		self.list.append((_("Images (backup)"), 9, _("تثبيت باكآب على صورة خام"), i))
		self.list.append((_("Lcd skins"), 10, _("سكينات الشاشة الامامية"), j))
		self.list.append((_("Multiboot"), 11, _("اضافات الخاصة بالاقلاع المتعدد و بالصور"), k))
		self.list.append((_("Novaler"), 12, _("اضافات الخاصة بجهاز نوفالر"), l))
		self.list.append((_("Panels"), 13, _("بانلات مختلفة"), m))
		self.list.append((_("Picons"), 14, _("شعارات القنوات"), n))
		self.list.append((_("Radiologos"), 15, _("خلفيات لقنوات الراديو"), o))
		self.list.append((_("Settings"), 16, _("ملفات قنوات ترددات و اعدادات التيونر"), p))
		self.list.append((_("Skins"), 17, _("سكينات"), q))
		self.list.append((_("Softcams"), 18, _("كامات و ملفات التشفير "), r))
		self.list.append((_("Spinners"), 19, _("شعار المتحرك اعلى الشاشة يسارا"), s))
		self.list.append((_("Systemplugins"), 20, _("بلاجينات و اضافات السيستام"), t))

		if self.indexpos != None:
			self["menu"].setIndex(self.indexpos)
		self["menu"].setList(self.list)
		
		
	def keyOK(self, item = None):
		self.indexpos = self["menu"].getIndex()
		if item == None:
			item = self["menu"].getCurrent()[1]
			self.select_item(item)

	def select_item(self, item):
		if item:
			if item is 1:
				self.session.open(allinone)
			elif item is 2:
				self.session.open(dependencies)
			elif item is 3:
				self.session.open(display)
			elif item is 4:
				self.session.open(drivers)
			elif item is 5:
				self.session.open(extensions)
			elif item is 6:
				self.session.open(feeds)
			elif item is 7:
				self.session.open(free)
			elif item is 8:
				self.session.open(imagesd)
			elif item is 9:
				self.session.open(imagesb)
			elif item is 10:
				self.session.open(lcdskins)
			elif item is 11:
				self.session.open(multiboot)
			elif item is 12:
				self.session.open(novaler)
			elif item is 13:
				self.session.open(panels)
			elif item is 14:
				self.session.open(picons)
			elif item is 15:
				self.session.open(radiologos)
			elif item is 16:
				self.session.open(settings)
			elif item is 17:
				self.session.open(skins)
			elif item is 18:
				self.session.open(softcams)
			elif item is 19:
				self.session.open(spinners)
			elif item is 20:
				self.session.open(systemplugins)

			else:
				self.close(None)

	def keyNumberGlobal(self, number):
			print('pressed', number)
			if number == 0:
				self.session.open(Console, _("Updating ElieSatPanel, please wait..."), [
            "wget --no-check-certificate https://raw.githubusercontent.com/eliesat/xml/main/installer.sh -qO - | /bin/sh"
        ])
			else:
				return

	def exit(self):
		self.close()


	def iptv(self):
		PY3 = sys.version_info.major >= 3
		if sys.version_info[0] < 3:
			from Plugins.Extensions.ElieSatPanel.sus.py2 import iptv2
			self.session.open(iptv2)
		else:
			from Plugins.Extensions.ElieSatPanel.sus.py3 import iptv3
			self.session.open(iptv3)

	def cccam(self):
		PY3 = sys.version_info.major >= 3
		if sys.version_info[0] < 3:
			from Plugins.Extensions.ElieSatPanel.sus.cpy2 import cccam2
			self.session.open(cccam2)
		else:
			from Plugins.Extensions.ElieSatPanel.sus.cpy3 import cccam3
			self.session.open(cccam3)

	def grid(self):
		try:
			from Plugins.Extensions.AJPan.plugin import CCVtWv
			if fileExists("/usr/lib/enigma2/python/Plugins/Extensions/AJPan/eliesat-panel/autoupdate-panel.sh"):
				self.session.open(CCVtWv)
		except:
				self.session.open(MessageBox, _('Install Ajpanel_Eliesatpanel and try again...'), MessageBox.TYPE_ERROR)
	def scriptslist(self):
				self.session.open(Scripts)
	def infoKey (self):
		self.session.open(Console, _("Please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/scripts/-/raw/main/check/_check-all.sh -qO - | /bin/sh"
        ])

	def getLivestreamerVersion(self):
		if fileExists("/usr/lib/python2.7/site-packages/livestreamer/__init__.py"):
			for line in open("/usr/lib/python2.7/site-packages/livestreamer/__init__.py"):
				if '__version__' in line:
					self["livestreamer"].text = line.split('"')[1]
		else:
			self["livestreamer"].text = _("Not Installed")

	def network_info(self):
		self.iConsole.ePopen("ifconfig -a", self.network_result)
		
	def network_result(self, result, retval, extra_args):
		if retval is 0:
			ip = ''
			mac = []
			if len(result) > 0:
				for line in result.splitlines(True):
					if 'HWaddr' in line:
						mac.append('%s' % line.split()[-1].strip('\n'))
					elif 'inet addr:' in line and 'Bcast:' in line:
						ip = line.split()[1].split(':')[-1]
				self["macInfo"].text = '/'.join(mac)
			else:
				self["macInfo"].text =  _("unknown")
		else:
			self["macInfo"].text =  _("unknown")
		if ip is not '':
			self["ipInfo"].text = ip
		else:
			self["ipInfo"].text = _("unknown")

	def getGStreamerVersionString(self):
		import enigma
		try:
			self["gstreamer"].text =  enigma.getGStreamerVersionString().strip('GStreamer ')
		except:
			self["gstreamer"].text =  _("unknown")
		
			
	def getPythonVersionString(self):
		try:
			import subprocess
			status, output = subprocess.getstatusoutput("python -V")
			self["python"].text =  output.split(' ')[1]
		except:
			self["python"].text =  _("unknown")
		
	def cpuinfo(self):
		if fileExists("/proc/cpuinfo"):
			cpu_count = 0
			processor = cpu_speed = cpu_family = cpu_variant = temp = ''
			core = _("core")
			cores = _("cores")
			for line in open('/proc/cpuinfo'):
				if "system type" in line:
					processor = line.split(':')[-1].split()[0].strip().strip('\n')
				elif "cpu MHz" in line:
					cpu_speed =  line.split(':')[-1].strip().strip('\n')
					#cpu_count += 1
				elif "cpu type" in line:
					processor = line.split(':')[-1].strip().strip('\n')
				elif "model name" in line:
					processor = line.split(':')[-1].strip().strip('\n').replace('Processor ', '')
				elif "cpu family" in line:
					cpu_family = line.split(':')[-1].strip().strip('\n')
				elif "cpu variant" in line:
					cpu_variant = line.split(':')[-1].strip().strip('\n')
				elif line.startswith('processor'):
					cpu_count += 1
			if not cpu_speed:
				try:
					cpu_speed = int(open("/sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_max_freq").read()) / 1000
				except:
					try:
						import binascii
						cpu_speed = int(int(binascii.hexlify(open('/sys/firmware/devicetree/base/cpus/cpu@0/clock-frequency', 'rb').read()), 16) / 100000000) * 100
					except:
						cpu_speed = '-'
			if fileExists("/proc/stb/sensors/temp0/value") and fileExists("/proc/stb/sensors/temp0/unit"):
				temp = "%s%s%s" % (open("/proc/stb/sensors/temp0/value").read().strip('\n'), chr(176).encode("latin-1"), open("/proc/stb/sensors/temp0/unit").read().strip('\n'))
			elif fileExists("/proc/stb/fp/temp_sensor_avs"):
				temp = "%s%sC" % (open("/proc/stb/fp/temp_sensor_avs").read().strip('\n'), chr(176).encode("latin-1"))
			if cpu_variant is '':
				self["CPU"].text = _("%s, %s Mhz (%d %s) %s") % (processor, cpu_speed, cpu_count, cpu_count > 1 and cores or core, temp)
			else:
				self["CPU"].text = "%s(%s), %s %s" % (processor, cpu_family, cpu_variant, temp)
		else:
			self["CPU"].text = _("undefined")

	def status(self):
		status = ''
		if fileExists("/usr/lib/opkg/status"):
			status = "/usr/lib/opkg/status"
		elif fileExists("/usr/lib/ipkg/status"):
			status = "/usr/lib/ipkg/status"
		elif fileExists("/var/lib/opkg/status"):
			status = "/var/lib/opkg/status"
		elif fileExists("/var/opkg/status"):
			status = "/var/opkg/status"
		return status
		
	def devices(self):
		list = ""
		hddlist = harddiskmanager.HDDList()
		hddinfo = ""
		if hddlist:
			for count in range(len(hddlist)):
				hdd = hddlist[count][1]
				if int(hdd.free()) > 1024:
					list += ((_("%s  %s  (%d.%03d GB free)\n") % (hdd.model(), hdd.capacity(), hdd.free()/1024 , hdd.free()%1024)))
				else:
					list += ((_("%s  %s  (%03d MB free)\n") % (hdd.model(), hdd.capacity(),hdd.free())))
		else:
			hddinfo = _("none")
		self["device"].text = list
		
	def HardWareType(self):
		if os.path.isfile("/proc/stb/info/boxtype"):
			return open("/proc/stb/info/boxtype").read().strip().upper()
		if os.path.isfile("/proc/stb/info/vumodel"):
			return "VU+" + open("/proc/stb/info/vumodel").read().strip().upper()
		if os.path.isfile("/proc/stb/info/model"):
			return open("/proc/stb/info/model").read().strip().upper()
		return _("unavailable")
		
	def getImageTypeString(self):
		try:
			if os.path.isfile("/etc/issue"):
				for line in open("/etc/issue"):
					if not line.startswith('Welcom') and '\l' in line:
						return line.capitalize().replace('\n', ' ').replace('\l', ' ').strip()
		except:
			pass
		return _("undefined")
		
	def getKernelVersionString(self):
		try:
			return open("/proc/version").read().split()[2]
		except:
			return _("unknown")
			
	def getImageVersionString(self):
		try:
			if os.path.isfile('/var/lib/opkg/status'):
				st = os.stat('/var/lib/opkg/status')
			elif os.path.isfile('/usr/lib/ipkg/status'):
				st = os.stat('/usr/lib/ipkg/status')
			elif os.path.isfile('/usr/lib/opkg/status'):
				st = os.stat('/usr/lib/opkg/status')
			elif os.path.isfile('/var/opkg/status'):
				st = os.stat('/var/opkg/status')
			tm = time.localtime(st.st_mtime)
			if tm.tm_year >= 2011:
				return time.strftime("%Y-%m-%d %H:%M:%S", tm)
		except:
			pass
		return _("unavailable")
		
			
	def mainInfo(self):
		package = 0
		self["Hardware"].text = self.HardWareType()
		self["Image"].text = self.getImageTypeString()
		self["Kernel"].text = self.getKernelVersionString()
		self["EnigmaVersion"].text = self.getImageVersionString()
		if fileExists(self.status()):
			for line in open(self.status()):
				if "-dvb-modules" in line and "Package:" in line:
					package = 1
				elif "kernel-module-player2" in line and "Package:" in line:
					package = 1
				elif "formuler-dvb-modules" in line and "Package:" in line:
					package = 1
				elif "vuplus-dvb-proxy-vusolo4k" in line and "Package:" in line:
					package = 1
				if "Version:" in line and package == 1:
					package = 0
					self["driver"].text = line.split()[-1]
					break

	def memInfo(self):
		for line in open("/proc/meminfo"):
			if "MemTotal:" in line:
				memtotal = line.split()[1]
			elif "MemFree:" in line:
				memfree = line.split()[1]
			elif "SwapTotal:" in line:
				swaptotal =  line.split()[1]
			elif "SwapFree:" in line:
				swapfree = line.split()[1]
		self["memTotal"].text = _("Total: %s Kb  Free: %s Kb") % (memtotal, memfree)
		self["swapTotal"].text = _("Total: %s Kb  Free: %s Kb") % (swaptotal, swapfree)
		
	def FlashMem(self):
		size = avail = 0
		st = os.statvfs("/")
		avail = st.f_bsize * st.f_bavail / 1024
		size = st.f_bsize * st.f_blocks / 1024
		self["flashTotal"].text = _("Total: %s Kb  Free: %s Kb") % (size , avail)
		
	def cancel(self):
		self.close()

	def update_me(self):
		remote_version = '0.0'
		remote_changelog = ''
		req = compat_Request(installer, headers={'User-Agent': 'Mozilla/5.0'})
		page = compat_urlopen(req).read()
		if PY3:
			data = page.decode("utf-8")
		else:
			data = page.encode("utf-8")
		if data:
			lines = data.split("\n")
			for line in lines:
				if line.startswith("version"):
					remote_version = line.split("=")
					remote_version = line.split("'")[1]
				if line.startswith("changelog"):
					remote_changelog = line.split("=")
					remote_changelog = line.split("'")[1]
					break

		if float(Version) < float(remote_version):
			new_version = remote_version
			new_changelog = remote_changelog
			self.session.openWithCallback(self.install_update, MessageBox, _("New version %s is available. \n %s \n\nDo you want to install it now?" % (new_version, new_changelog)), MessageBox.TYPE_YESNO)

	def install_update(self, answer=False):
		if answer:
			self.session.open(Console, title='Updating please wait...', cmdlist='wget -q "--no-check-certificate" ' + installer + ' -O - | /bin/sh', finishedCallback=self.myCallback, closeOnSuccess=False)

	def myCallback(self, result):
		return

	def intInfo(self):
		try:
			import socket
			socket.setdefaulttimeout(0.5)
			socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(('8.8.8.8', 53))
			self["internet"].text = _("Connected")
			return True
		except:
			self["internet"].text = _("Disconnected")
			return False
		if os.system("ping -c 1 8.8.8.8 "):
			self["internet"].text = _("Connected")
		else:
			self["internet"].text = _("Disconnected")
		return

class Scripts(Screen):
	skin = """
<screen name="Scripts" position="0,0" size="1920,1080" backgroundColor="transparent" flags="wfNoBorder" title="Scripts">

<ePixmap position="0,0" zPosition="-1" size="1920,1080" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ElieSatPanel/images/bglist.png"/>
  
<widget name="list" position="48,200" size="1240,660" font="Regular;35" halign="center" valign="center" render="Listbox" itemHeight="66" selectionPixmap="/usr/lib/enigma2/python/Plugins/Extensions/ElieSatPanel/images/selection.png" transparent="1" scrollbarMode="showOnDemand" />

<!-- title -->
<eLabel text="Scripts lists" position="560,120" size="400,50" zPosition="1" font="Regular;40" halign="left" backgroundColor="background" foregroundColor="foreground" transparent="1" />
<ePixmap position="473,125" size="180,47" zPosition="1" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ElieSatPanel/images/2.png" alphatest="blend" />
<ePixmap position="800,125" size="180,47" zPosition="1" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ElieSatPanel/images/2.png" alphatest="blend" />

<!-- title2 -->
<eLabel text="Select and press ok to execute" position="380,880" size="700,50" zPosition="1" font="Regular;40" halign="left" backgroundColor="background" foregroundColor="foreground" transparent="1" />
<ePixmap position="310,880" size="180,47" zPosition="1" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ElieSatPanel/images/2.png" alphatest="blend" />

<!-- title3 -->
<widget name="Panel" position="1365,650" size="270,50" font="Regular;40" halign="center" valign="center" backgroundColor="background" foregroundColor="foreground" transparent="1"/>
<widget name="Version" position="1610,650" size="150,50" font="Regular;35" halign="center" valign="center" backgroundColor="background" foregroundColor="foreground" transparent="1"/>
<ePixmap position="1280,650" size="180,47" zPosition="1" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ElieSatPanel/images/2.png" alphatest="blend" />

<!-- minitv -->
<widget source="session.VideoPicture" render="Pig" position="1305,195" size="550,400" zPosition="1" backgroundColor="#ff000000" />

<!-- clock -->
<widget source="global.CurrentTime" render="Label" position="1290,100" size="350,90" font="lsat; 75" noWrap="1" halign="center" valign="bottom" backgroundColor="background" foregroundColor="foreground" transparent="1" zPosition="2">
		<convert type="ClockToText">Default</convert>

<!-- calender -->
</widget>
<widget source="global.CurrentTime" render="Label" position="1530,105" size="335,54" font="lsat; 24" halign="center" valign="bottom" backgroundColor="background" foregroundColor="foreground" transparent="1" zPosition="1">
<convert type="ClockToText">Format %A %d %B</convert>
</widget>

<!-- button -->
<ePixmap position="120,1015" zPosition="1" size="240,10" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ElieSatPanel/images/red.png" alphatest="blend" />
<widget source="key_red" render="Label" position="160,960" zPosition="2" size="165,45" font="Regular;35" halign="center" valign="center" backgroundColor="background" foregroundColor="foreground" transparent="1" />
<ePixmap position="400,1015" zPosition="1" size="240,10" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ElieSatPanel/images/green.png" alphatest="blend" />
<widget source="key_green" render="Label" position="387.5,960" zPosition="2" size="265,45" font="Regular;35" halign="center" valign="center" backgroundColor="background" foregroundColor="foreground" transparent="1" />
<ePixmap position="680,1015" zPosition="1" size="240,10" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ElieSatPanel/images/yellow.png" alphatest="blend" />
<widget source="key_yellow" render="Label" position="720,960" zPosition="2" size="165,45" font="Regular;35" halign="center" valign="center" backgroundColor="background" foregroundColor="foreground" transparent="1" />
<ePixmap position="960,1015" zPosition="1" size="240,10" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ElieSatPanel/images/blue.png" alphatest="blend" />
<widget source="key_blue" render="Label" position="1000,960" zPosition="2" size="165,45" font="Regular;35" halign="center" valign="center" backgroundColor="background" foregroundColor="foreground" transparent="1" />
    <eLabel backgroundColor="#00ffffff" position="55,860" size="1220,3" zPosition="2" />
    <eLabel backgroundColor="#00ffffff" position="55,195" size="1220,3" zPosition="2" />

<!-- ip address -->
<widget source="ipLabel" render="Label" position="1350,755" zPosition="2" size="180,40" font="Regular;35" halign="right" valign="center" backgroundColor="background" foregroundColor="foreground" transparent="1" />
	<widget source="ipInfo" render="Label" position="1540,755" zPosition="2" size="390,40" font="Regular;35" halign="left" valign="center" backgroundColor="background" foregroundColor="foreground" transparent="1" />
<ePixmap position="1280,750" size="180,47" zPosition="1" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ElieSatPanel/images/2.png" alphatest="blend" />

<!-- internet -->
	<widget source="internet" render="Label" position="1540,805" zPosition="2" size="390,40" font="Regular;35" halign="left" valign="center" backgroundColor="background" foregroundColor="foreground" transparent="1" />
<widget source="internetLabel" render="Label" position="1350,805" zPosition="2" size="180,40" font="Regular;35" halign="right" valign="center" backgroundColor="background" foregroundColor="foreground" transparent="1" />
<ePixmap position="1280,800" size="180,47" zPosition="1" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ElieSatPanel/images/2.png" alphatest="blend" />

<!-- path -->
<eLabel text="Path: /usr/script/" position="1390,855" size="400,50" zPosition="1" font="Regular;35" halign="left" backgroundColor="background" foregroundColor="foreground" transparent="1" />
<ePixmap position="1280,850" size="180,47" zPosition="1" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ElieSatPanel/images/2.png" alphatest="blend" />
</screen>"""

	def __init__(self, session):
		Screen.__init__(self, session)
		self.session = session
		self.script, self.name = '', ''
		self.setTitle(_("Script Executer"))
		self.iConsole = iConsole()
		self.script_menu()
		self["key_red"] = StaticText(_("Remove"))
		self["key_green"] = StaticText(_("Update"))
		self["key_yellow"] = StaticText(_("Uninstall"))
		self["key_blue"] = StaticText(_("Restart E2"))
		self["ipLabel"] = StaticText(_("Local  IP:"))
		self["ipInfo"] = StaticText()
		self["macInfo"] = StaticText()
		self["internetLabel"] = StaticText(_("Internet:"))
		self["internet"] = StaticText()
		self["Version"] = Label(_("V" + Version))
		self["Panel"] = Label(_(Panel))
		self.intInfo()
		self.network_info()
		self["actions"] = ActionMap(["OkCancelActions","ColorActions"], {"ok": self.run, "green": self.update, "yellow": self.bgrun, "red": self.remove, "blue": self.restart, "cancel": self.close}, -1)
	def script_menu(self):
		list = []
		if pathExists(scriptpath):
			list = os.listdir("%s" % scriptpath[:-1])
			list = [x for x in list if x.endswith('.sh') or x.endswith('.py')]
		else:
			list = []
		list.sort()
		self["list"] = MenuList(list)
	
	def bgrun(self):
				self.session.open(ui)

	def run(self):
		self.script = self["list"].getCurrent()
		if self.script is not None:
			self.name = "%s%s" % (scriptpath, self.script)
			if self.name.endswith('.sh'):
				os.chmod('%s' %  self.name, 0o755)
			else:
				self.name = 'python %s' % self.name
			self.session.open(Console, self.script.replace("_", " "), cmdlist=[self.name])

	def restart (self):
				self.session.open(Console, _("Restarting enigma2 please wait..."), [
            "[ command -v dpkg &> /dev/null ] && systemctl restart enigma2 || killall -9 enigma2"
        ])

	def network_info(self):
		self.iConsole.ePopen("ifconfig -a", self.network_result)
		
	def network_result(self, result, retval, extra_args):
		if retval is 0:
			ip = ''
			mac = []
			if len(result) > 0:
				for line in result.splitlines(True):
					if 'HWaddr' in line:
						mac.append('%s' % line.split()[-1].strip('\n'))
					elif 'inet addr:' in line and 'Bcast:' in line:
						ip = line.split()[1].split(':')[-1]
				self["macInfo"].text = '/'.join(mac)
			else:
				self["macInfo"].text =  _("unknown")
		else:
			self["macInfo"].text =  _("unknown")
		if ip is not '':
			self["ipInfo"].text = ip
		else:
			self["ipInfo"].text = _("unknown")

	def intInfo(self):
		try:
			import socket
			socket.setdefaulttimeout(0.5)
			socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(('8.8.8.8', 53))
			self["internet"].text = _("Connected")
			return True
		except:
			self["internet"].text = _("Disconnected")
			return False
		if os.system("ping -c 1 8.8.8.8 "):
			self["internet"].text = _("Connected")
		else:
			self["internet"].text = _("Disconnected")
		return
	def exit(self):
		self.close()

	def remove(self):
		os.system('rm -rf /usr/script/*')
		self.session.open(MessageBox,(_("Remove of scripts lists is done , press the green button to reinstall")), MessageBox.TYPE_INFO, timeout = 4 )
	def update(self):
				self.session.open(Console, _("Installing scripts please wait..."), [
            "wget --no-check-certificate https://raw.githubusercontent.com/eliesat/scripts/main/installer.sh -qO - | /bin/sh"
        ])

#######################################
def status_path():
	status = '/usr/lib/opkg/status'
	if fileExists("/usr/lib/ipkg/status"):
		status = "/usr/lib/ipkg/status"
	elif fileExists("/var/lib/opkg/status"):
		status = "/var/lib/opkg/status"
	elif fileExists("/var/opkg/status"):
		status = "/var/opkg/status"
	return status

class ui(Screen):
	skin = """
<screen name="uninstall" position="0,0" size="1920,1080" backgroundColor="transparent" flags="wfNoBorder" title="ElieSatPanel">
<ePixmap position="0,0" zPosition="-1" size="1920,1080" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ElieSatPanel/images/bglist.png"/>
<!-- title -->
<eLabel text="Installed plugins lists" position="460,120" size="400,50" zPosition="1" font="Regular;39" halign="left" backgroundColor="background" foregroundColor="foreground" transparent="1" />
<ePixmap position="370,125" size="180,47" zPosition="1" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ElieSatPanel/images/2.png" alphatest="blend" />
<ePixmap position="880,125" size="180,47" zPosition="1" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ElieSatPanel/images/2.png" alphatest="blend" />

<!-- title2 -->
<eLabel text="Select and press ok to remove" position="380,880" size="700,50" zPosition="1" font="Regular;40" halign="left" backgroundColor="background" foregroundColor="foreground" transparent="1" />
<ePixmap position="310,880" size="180,47" zPosition="1" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ElieSatPanel/images/2.png" alphatest="blend" />
    <eLabel backgroundColor="#00ffffff" position="55,860" size="1220,3" zPosition="2" />
    <eLabel backgroundColor="#00ffffff" position="55,195" size="1220,3" zPosition="2" />
<!-- title3 -->
<widget name="Panel" position="1365,650" size="270,50" font="Regular;40" halign="center" valign="center" backgroundColor="background" foregroundColor="foreground" transparent="1"/>
<widget name="Version" position="1610,650" size="150,50" font="Regular;35" halign="center" valign="center" backgroundColor="background" foregroundColor="foreground" transparent="1"/>
<ePixmap position="1280,650" size="180,47" zPosition="1" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ElieSatPanel/images/2.png" alphatest="blend" />
<!-- minitv -->
<widget source="session.VideoPicture" render="Pig" position="1305,195" size="550,400" zPosition="1" backgroundColor="#ff000000" />
<!-- clock -->
<widget source="global.CurrentTime" render="Label" position="1290,100" size="350,90" font="lsat; 75" noWrap="1" halign="center" valign="bottom" backgroundColor="background" foregroundColor="foreground" transparent="1" zPosition="2">
		<convert type="ClockToText">Default</convert>
<!-- calender -->
</widget>
<widget source="global.CurrentTime" render="Label" position="1530,105" size="335,54" font="lsat; 24" halign="center" valign="bottom" backgroundColor="background" foregroundColor="foreground" transparent="1" zPosition="1">
<convert type="ClockToText">Format %A %d %B</convert>
</widget>

<!-- menu  -->
<widget source="menu" selectionPixmap="/usr/lib/enigma2/python/Plugins/Extensions/ElieSatPanel/images/selection.png" render="Listbox" position="48,200" size="1240,660"  transparent="1">
	<convert type="TemplatedMultiContent">
		{"template": [
			MultiContentEntryText(pos = (120, 10), size = (900, 45), font=0, flags = RT_HALIGN_LEFT, text = 0), # index 2 is the Menu Titel
			MultiContentEntryText(pos = (1030, 19), size = (163, 35), font=1, flags = RT_HALIGN_LEFT, text = 1), # index 3 is the Description
			MultiContentEntryPixmapAlphaTest(pos = (25, 5), size = (50, 40), png = 2), # index 4 is the pixmap
				],
	"fonts": [gFont("Regular", 35),gFont("Regular", 25)],
	"itemHeight": 66
	}
	</convert>
	</widget>
<ePixmap position="120,1015" zPosition="1" size="240,10" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ElieSatPanel/images/red.png" alphatest="blend" />
<widget source="key_red" render="Label" position="160,960" zPosition="2" size="165,45" font="Regular;35" halign="center" valign="center" backgroundColor="background" foregroundColor="foreground" transparent="1" />
<ePixmap position="400,1015" zPosition="1" size="240,10" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ElieSatPanel/images/green.png" alphatest="blend" />
<widget source="key_green" render="Label" position="387.5,960" zPosition="2" size="265,45" font="Regular;35" halign="center" valign="center" backgroundColor="background" foregroundColor="foreground" transparent="1" />
<!-- ip address -->
<widget source="ipLabel" render="Label" position="1350,755" zPosition="2" size="180,40" font="Regular;35" halign="right" valign="center" backgroundColor="background" foregroundColor="foreground" transparent="1" />
	<widget source="ipInfo" render="Label" position="1540,755" zPosition="2" size="390,40" font="Regular;35" halign="left" valign="center" backgroundColor="background" foregroundColor="foreground" transparent="1" />
<ePixmap position="1280,750" size="180,47" zPosition="1" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ElieSatPanel/images/2.png" alphatest="blend" />

<!-- internet -->
	<widget source="internet" render="Label" position="1540,805" zPosition="2" size="390,40" font="Regular;35" halign="left" valign="center" backgroundColor="background" foregroundColor="foreground" transparent="1" />
<widget source="internetLabel" render="Label" position="1350,805" zPosition="2" size="180,40" font="Regular;35" halign="right" valign="center" backgroundColor="background" foregroundColor="foreground" transparent="1" />
<ePixmap position="1280,800" size="180,47" zPosition="1" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ElieSatPanel/images/2.png" alphatest="blend" />
</screen>"""
	  
	def __init__(self, session, args=None):
		Screen.__init__(self, session)
		self.setTitle(_("Ipk remove"))
		self.session = session
		self.path = status_path()
		self.iConsole = iConsole()
		self.status = False
		self["key_red"] = StaticText(_("Close"))
		self["key_green"] = StaticText(_("UnInstall"))
		self.list = []
		self["menu"] = List(self.list)
		self.nList()
		self["ipLabel"] = StaticText(_("Local  IP:"))
		self["ipInfo"] = StaticText()
		self["macInfo"] = StaticText()
		self["internetLabel"] = StaticText(_("Internet:"))
		self["internet"] = StaticText()
		self.intInfo()
		self.network_info()
		self["Version"] = Label(_("V" + Version))
		self["Panel"] = Label(_(Panel))
		self["actions"] = ActionMap(["OkCancelActions", "ColorActions"],
			{
				"cancel": self.cancel,
				"ok": self.remove_ipk,
				"green": self.remove_ipk,
				"red": self.cancel,
			},-1)
		
	def nList(self):
		self.list = []
		ipkminipng = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/images/1.png"))
		for line in open(status_path()):
			if "Package:" in line:
				name1 = line.replace("\n","").split()[-1]
			elif "Version:" in line:
				name2 = line.split()[-1] + "\n"
			elif "Status:" in line and not "not-installed" in line:
				self.list.append((name1, name2, ipkminipng))
		self.list.sort()
		self["menu"].setList(self.list)

	def cancel(self):
		self.close()
		
	def remove_ipk(self):
		local_status = ipk_dir = ''
		pkg_name = self["menu"].getCurrent()[0]
		if self.status:
			local_status = '-force-remove'
			self.staus = False
		if 'plugin' in pkg_name or 'skin' in pkg_name:
			if fileExists('%s%s.list' % (self.path[:-6] + 'info/', pkg_name)):
				for line in open('%s%s.list' % (self.path[:-6] + 'info/', pkg_name)):
					if 'plugin.py' in line or 'plugin.pyo' in line:
						ipk_dir = line[:-11]
					elif 'skin.xml' in line:
						ipk_dir = line[:-10]
		self.session.open(Console, title = _("%s" % ipk_dir), cmdlist = ["opkg remove --force-depends %s %s" % (local_status, pkg_name)], closeOnSuccess = False)
		if pathExists(ipk_dir):
			self.iConsole.ePopen("rm -rf %s" % ipk_dir, self.finish)
		else:
			self.nList()
	def network_info(self):
		self.iConsole.ePopen("ifconfig -a", self.network_result)
		
	def network_result(self, result, retval, extra_args):
		if retval is 0:
			ip = ''
			mac = []
			if len(result) > 0:
				for line in result.splitlines(True):
					if 'HWaddr' in line:
						mac.append('%s' % line.split()[-1].strip('\n'))
					elif 'inet addr:' in line and 'Bcast:' in line:
						ip = line.split()[1].split(':')[-1]
				self["macInfo"].text = '/'.join(mac)
			else:
				self["macInfo"].text =  _("unknown")
		else:
			self["macInfo"].text =  _("unknown")
		if ip is not '':
			self["ipInfo"].text = ip
		else:
			self["ipInfo"].text = _("unknown")

	def intInfo(self):
		try:
			import socket
			socket.setdefaulttimeout(0.5)
			socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(('8.8.8.8', 53))
			self["internet"].text = _("Connected")
			return True
		except:
			self["internet"].text = _("Disconnected")
			return False
		if os.system("ping -c 1 8.8.8.8 "):
			self["internet"].text = _("Connected")
		else:
			self["internet"].text = _("Disconnected")
		return


	def finish(self, result, retval, extra_args):
		self.nList()
