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
<ePixmap position="73,125" size="180,47" zPosition="1" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ElieSatPanel/images/1.png" alphatest="blend" />

<!-- title1 -->
<eLabel text="Extensions" position="1490,700" size="400,50" zPosition="1" font="Regular;40" halign="left" foregroundColor="white" backgroundColor="#ff2c2d2b" transparent="1" />

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
		MultiContentEntryText(pos = (640, 19), size = (600, 35), font=1, flags = RT_HALIGN_LEFT, text = 2), # index 3 is the Description
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
		pa = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/images/1.png"))
		pb = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/images/1.png"))
		pc = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/images/1.png"))
		pd = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/images/1.png"))
		pe = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/images/1.png"))
		pf = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/images/1.png"))
		pg = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/images/1.png"))
		ph = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/images/1.png"))
		pi = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/images/1.png"))
		pj = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/images/1.png"))
		pk = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/images/1.png"))
		pl = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/images/1.png"))
		pm = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/images/1.png"))
		pn = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/images/1.png"))
		po = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/images/1.png"))
		pp = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/images/1.png"))
		pq = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/images/1.png"))
		pr = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/images/1.png"))
		ps = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/images/1.png"))
		pt = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/images/1.png"))
		pu = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/images/1.png"))
		pv = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/images/1.png"))
		pw = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/images/1.png"))
		px = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/images/1.png"))
		py = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/images/1.png"))
		pz = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/images/1.png"))
		pA = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/images/1.png"))
		pB = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/images/1.png"))
		pC = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/images/1.png"))
		pD = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/images/1.png"))
		pE = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/images/1.png"))
		pF = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/images/1.png"))
		pG = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/images/1.png"))
		pH = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/images/1.png"))
		pI = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/images/1.png"))
		pJ = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/images/1.png"))
		pK = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/images/1.png"))
		pL = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/images/1.png"))
		pM = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/images/1.png"))
		pN = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/images/1.png"))
		pO = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/images/1.png"))
		pP = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/images/1.png"))
		pQ = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/images/1.png"))
		pR = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/images/1.png"))
		pS = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/images/1.png"))
		pT = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/images/1.png"))
		pU = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/images/1.png"))
		pV = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/images/1.png"))
		pW = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/images/1.png"))
		pX = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/images/1.png"))
		pY = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/images/1.png"))
		pZ = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/images/1.png"))
		aa = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/images/1.png"))
		ab = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/images/1.png"))
		ac = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/images/1.png"))
		ad = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/images/1.png"))
		ae = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/images/1.png"))
		af = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/images/1.png"))
		ag = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/images/1.png"))
		ah = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/images/1.png"))
		ai = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/images/1.png"))

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
		self.list.append((_("Backupflashe-9.5"), 11, _("باكآب الصورة"), k))
		self.list.append((_("Bissfeedautokey-2.8"), 12, _("خاص بالفيدات و شفرات البيس"), l))
		self.list.append((_("Bitrate-2.0"), 13, _("عرض معدل البت لقنوات السات على الشاشة"), m))
		self.list.append((_("Bitrate-mod-ariad"), 14, _("عرض معدل البت لقنوات السات على الشاشة"), n))
		self.list.append((_("Bootlogokids-stony272"), 15, _("صور اقلاع للاطفال"), o))
		self.list.append((_("Bootlogoswapper-1.0"), 16, _("صور اقلاع eliesat-special-edition"), p))
		self.list.append((_("Bouquetmakerxtream-1.46"), 17, _("تحويل اشتراك الiptv لمفضلات"), q))
		self.list.append((_("Bundesliga-clock-1.0"), 18, _("تثبيت الساعة على الشاشة بشكل دائم"), r))
		self.list.append((_("Cacheflush-2.0r4"), 19, _("مسح ملفات الكاش من الذاكرة العشوائية"), s))
		self.list.append((_("Chlogochanger-1.0"), 20, _("تخصيص شعار للقنوات من اختيارك"), t))
		self.list.append((_("Cccamimfo-1.9"), 21, _("عرض معلومات السسكام"), u))
		self.list.append((_("Chocholousek-5.0.240904"), 22, _("تسطيب بيكونات"), v))
		self.list.append((_("Ciefpsettingsmotor-1.6"), 23, _("تنزيل و تثبيت ملف قنوات بافل سييف"), w))
		self.list.append((_("Crashlogviewer-1.5"), 24, _("تصفح ملفات الكراش"), x))
		self.list.append((_("Crondmanager-1.3"), 25, _("اضافة توقيت للسكريبت برسم التنفيذ"), y))
		self.list.append((_("Dreamexplorer-2024.08.21"), 26, _("مدير ملفات mod lululla"), z))
		self.list.append((_("E2iplayer"), 27, _("مشغل اي بي تي في mohamed_os"), A))
		self.list.append((_("E2m3ubouquet-2.0.1"), 28, _("تحويل الiptv لمفضلات mod-dorik"), B))
		self.list.append((_("Enigma2readeradder-1.0"), 113, _("كتابة سطر السسكام و تعريفه داخل الايميوهات"), i))
		self.list.append((_("Easy-cccam-0.2"), 29, _("اضافة اسطر cccam"), C))
		self.list.append((_("Epggrabber-24.3"), 30, _("الدليل الالكتروني"), D))
		self.list.append((_("Epggrabber-24.2-mod-elie"), 31, _("الدليل الالكتروني"), E))
		self.list.append((_("Epgimport-9.9"), 32, _("جلب الدليل الاكتروني و عرضه على لايحة القنوات"), F))
		self.list.append((_("Epgimport-1.9.1-mod-dorik"), 33, _("جلب الدليل الاكتروني و عرضه على لايحة القنوات"), G))
		self.list.append((_("Epgtranslator-1.4r2"), 34, _("ترجمة دليل الالكتروني"), H))
		self.list.append((_("Feedsfinder-3.1"), 35, _("خاص بالفيدات و شفرات البيس"), I))
		self.list.append((_("Filecommander-2024.08.31"), 36, _("مدير ملفات mod lululla"), J))
		self.list.append((_("Filmxy-1.4"), 37, _("اي بي تي في مجاني"), K))
		self.list.append((_("Footonsat-1.9"), 38, _("مواعيد مبارايات كرة القدم مع القنوات الناقلة"), L))
		self.list.append((_("Footonsat-1.9-mohamed_os"), 39, _("مواعيد مبارايات كرة القدم مع القنوات الناقلة"), M))
		self.list.append((_("Foreca-3.3"), 109, _("حالة الطقس"), ae))
		self.list.append((_("Freearhey-3.1"), 40, _("اي بي تي في مجاني"), N))
		self.list.append((_("Freeserver-8.3.8-r1"), 41, _("جلب اسطر سسكام مجانية و خدمات أخرى"), O))
		self.list.append((_("Gioppygio-12.2"), 42, _("تسطيب بيكونات و ملفات قنوات"), P))
		self.list.append((_("Hardwareinfo-5.2"), 111, _("معلومات عز الجهاز"), ag))
		self.list.append((_("Hasbahca-1.8"), 43, _("اي بي تي في مجاني"), Q))
		self.list.append((_("Historyzapselector-1.0.42"), 44, _("تصفح آخر قنوات سات قلبت فيهم mod dorik"), R))
		self.list.append((_("Horoscope-1.1"), 45, _("الابراج"), S))
		self.list.append((_("Imdb-2.1"), 46, _("عرض بوستر و معلومات فيلم لقناة لها دليل الكتروني"), T))
		self.list.append((_("Internetspeedtest-1.7"), 47, _("اختبار سرعة الاتصال بالانترنيت"), U))
		self.list.append((_("Ipaudio-6.8"), 48, _("اضافة الصوتيات على قنوات السات"), V))
		self.list.append((_("Ipaudio-7.4-ffmpeg"), 49, _("اضافة الصوتيات على قنوات السات"), W))
		self.list.append((_("Ipaudiopro-1.3"), 50, _("اضافة الصوتيات على قنوات السات py2 py3.9 py3.12"), X))
		self.list.append((_("Ipaudiopro-1.5"), 51, _("اضافة الصوتيات على قنوات السات"), Y))
		self.list.append((_("Ipchecker-004"), 52, _("عرض اي يي الرسيفر و الخارجي معا"), Z))
		self.list.append((_("Iptosat-1.8"), 53, _("مشاهدة قنوات الiptv على قنوات السات"), pa))
		self.list.append((_("Iptvarchive-2.0.89"), 54, _("معاينة ارشيف الاي بي تي في"), pb))
		self.list.append((_("Iptvdream-4.123"), 55, _("قارئ و مشغل ملفات m3u"), pc))
		self.list.append((_("Isettingse2-5.8"), 56, _("تسطيب ملفات قنوات py3.11"), pd))
		self.list.append((_("Jediepgxtream-2.12"), 57, _("تثبيت الدليل على قنوات ال اي يي تي في"), pe))
		self.list.append((_("Jedimakerxtream-6.40"), 58, _("مشاهدة الiptv بمفضلات السات"), pf))
		self.list.append((_("Keyadder-8.2"), 59, _("اضافة مفتاح او شفرة بيس على ملف السوفتكام"), pg))
		self.list.append((_("Lamedbmerger-1.0"), 60, _("دمج ملفين قنوات و اقمار ببعض بملف واحد py3.11"), ph))
		self.list.append((_("Mmpicons-1.4"), 61, _("تسطيب بيكونات"), pi))
		self.list.append((_("Moviebrowser-3.8"), 62, _("تصفح الافلام و المسلسلات المخزنة"), pj))
		self.list.append((_("Moviesmanager-1.0"), 63, _("تصفح الافلام و المسلسلات المخزنة"), pk))
		self.list.append((_("Multiquickbutton-2.7.15-r10"), 64, _("تخصيص وظائف لازرار الرومونت كوننرول py3-mod-raed"), pl))
		self.list.append((_("Multistalker-1.5"), 65, _("مشغل بورتلات اي بي تي في"), pm))
		self.list.append((_("Multistalkerpro-1.0"), 66, _("مشغل بورتلات اي بي تي في"), pn))
		self.list.append((_("Multistalkerpro-1.2"), 67, _("مشغل بورتلات اي بي تي في py3.12"), po))
		self.list.append((_("Mycam-7.0"), 68, _("اشتراك شيرينج مدفوع"), pp))
		self.list.append((_("Ncam-status-3.2"), 69, _("معلومات عن حالة المحاكي"), pq))
		self.list.append((_("Newpermanentclock-1.0"), 70, _("تثبيت الساعة على الشاشة بشكل دائم"), pr))
		self.list.append((_("Oaweather-3.0"), 71, _("حالة الطقس py3.11"), ps))
		self.list.append((_("Oscam-status-6.5"), 72, _("معلومات عن حالة المحاكي"), pt))
		self.list.append((_("Piconinstaller-24.08.23"), 73, _("تسطيب بيكونات"), pu))
		self.list.append((_("Pluginskinmover-0.8"), 74, _("نقل و قراءة البلاجينات على التخزين الخارجي"), pv))
		self.list.append((_("Plutotv-20240831"), 75, _("اي بي تي في مجاني"), pw))
		self.list.append((_("Quarter-pounder-6.2.0"), 76, _("تنشيط قنوات الاي بي تي في"), px))
		self.list.append((_("Quran-karim-2.2"), 77, _("القرآن الكريم"), py))
		self.list.append((_("Quran-0.2"), 78, _("القرآن الكريم mod raed"), pz))
		self.list.append((_("Radiom-1.1"), 79, _("ستريم لمحطات راديو"), pA))
		self.list.append((_("Radiogit-1.1"), 80, _("راديو"), pB))
		self.list.append((_("Raedquicksignal-17.6"), 81, _("مستكشف اشارة الترددات"), pC))
		self.list.append((_("Rakutentv-20240324"), 82, _("اي بي تي في مجاني"), pD))
		self.list.append((_("Samsungtvplus-20241116"), 83, _("اي بي تي في مجاني"), pE))
		self.list.append((_("Screengrabber-3.2"), 84, _("التقاط و تخزين صورة عن الشاشة"), pF))
		self.list.append((_("Screennames-1.06"), 85, _("عرض اسامي سكرينات السكين"), pG))
		self.list.append((_("Scriptexecuter-1.0"), 86, _("تصفح لايحة السكريبتات و تنفيذهم"), pH))
		self.list.append((_("Sherlockmod-1.4.2"), 87, _("اينفوبار اضافي"), pI))
		self.list.append((_("Shootyourscreen-0.3"), 88, _("التقاط و تخزين صورة عن الشاشة"), pJ))
		self.list.append((_("skin-e2sentials-1.0"), 110, _("اضافات على سكين المستخدم"), af))
		self.list.append((_("Spinnerselector-3.2"), 89, _("تسطيب سبينرات"), pK))
		self.list.append((_("Subssupport-1.5.8r9"), 90, _("الترجمة"), pL))
		self.list.append((_("Subssupport-1.7.0-r12"), 91, _("الترجمة"), pM))
		self.list.append((_("Theweather-2.5r0"), 92, _("حالة الطقس"), pN))
		self.list.append((_("Tmdb-8.6r7"), 93, _("عرض بوستر و معلومات فيلم"), pO))
		self.list.append((_("Transmission-5.0.9.9"), 94, _("مشاهدة و تنزيل افلام و مسلسلات"), pP))
		self.list.append((_("Vavoo-1.33"), 95, _("اي بي تي في مجاني"), pQ))
		self.list.append((_("Visualweather-1.10"), 96, _("حالة الطقس"), pR))
		self.list.append((_("Weathermsn-1.3r3"), 97, _("حالة الطقس"), pS))
		self.list.append((_("Weatherplugin-2.2"), 98, _("حالة الطقس"), pT))
		self.list.append((_("Weatherpluginicons-1.1"), 99, _("ايقونات بلاجين الطقس weatherplugin"), pU))
		self.list.append((_("Wireguard-vpn-15.1"), 100, _("اضافة اشتراك الvpn + معاينة سرعة النت"), pV))
		self.list.append((_("Worldcam-4.8"), 101, _("كاميرات من حول العالم"), pW))
		self.list.append((_("Xcplugin-forever-4.2"), 102, _("مشغل اي بي تي في"), pX))
		self.list.append((_("Xklass-1.36"), 103, _("مشغل اي بي تي في"), pY))
		self.list.append((_("Xstreamity-4.86"), 104, _("مشغل اي بي تي في"), pZ))
		self.list.append((_("Xtraevent-4.2"), 105, _("جلب بوسترات يعمل على السكينات الخاصة فيه"), aa))
		self.list.append((_("Xtraevent-4.5"), 106, _("جلب بوسترات يعمل على السكينات الخاصة فيه"), ab))
		self.list.append((_("Xtraevent-6.805"), 107, _("جلب بوسترات يعمل على السكينات الخاصة فيه"), ac))
		self.list.append((_("Youtube-2025.02.24"), 108, _("مشاهدة فيديوهات اليوتيوب"), ad))
		self.list.append((_("zaptimer-1.0"), 112, _("وضع توقيت للرجوع للقناة"), ah))

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
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/backupflashe/backupflashe.sh -qO - | /bin/sh"
        ])
			elif item is 12:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/bissfeedautokey/bissfeedautokey.sh -qO - | /bin/sh"
        ])
			elif item is 13:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/bitrate/bitrate.sh -qO - | /bin/sh"
        ])
			elif item is 14:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/bitrate/bitrate-mod-ariad.sh -qO - | /bin/sh"
        ])
			elif item is 15:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/bootlogokids/bootlogokids-stony272.sh -qO - | /bin/sh"
        ])
			elif item is 16:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/bootlogoswapper/bootlogoswapper-eliesat-special-edition.sh -qO - | /bin/sh"
        ])
			elif item is 17:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/bouquetmakerxtream/bouquetmakerxtream.sh -qO - | /bin/sh"
        ])
			elif item is 18:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/bundesliga-permanent-clock/bundesliga-permanent-clock.sh -qO - | /bin/sh"
        ])
			elif item is 19:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/cacheflush/cacheflush.sh -qO - | /bin/sh"
        ])
			elif item is 20:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/chlogochanger/chlogochanger.sh -qO - | /bin/sh"
        ])
			elif item is 21:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/cccaminfo/cccaminfo.sh -qO - | /bin/sh"
        ])
			elif item is 22:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/chocholousek-picons/chocholousek-picons.sh -qO - | /bin/sh"
        ])
			elif item is 23:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/ciefpsettingsmotor/ciefpsettingsmotor.sh -qO - | /bin/sh"
        ])
			elif item is 24:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/crashlogviewer/crashlogviewer.sh -qO - | /bin/sh"
        ])
			elif item is 25:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/crondmanager/crondmanager.sh -qO - | /bin/sh"
        ])
			elif item is 26:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/dreamexplorer/dreamexplorer.sh -qO - | /bin/sh"
        ])
			elif item is 27:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/e2iplayer/e2iplayer-main.sh -qO - | /bin/sh"
        ])
			elif item is 28:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/e2m3u2bouquet/e2m3u2bouquet.sh -qO - | /bin/sh"
        ])
			elif item is 29:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/easy-cccam/easy-cccam.sh -qO - | /bin/sh"
        ])
			elif item is 30:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/epggrabber2/epggrabber.sh -qO - | /bin/sh"
        ])
			elif item is 31:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/epggrabber/epggrabber.sh -qO - | /bin/sh"
        ])
			elif item is 32:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/epgimport/epgimport.sh -qO - | /bin/sh"
        ])
			elif item is 33:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/epgimport-mod-dorik1972/epgimport-mod-dorik1972.sh -qO - | /bin/sh"
        ])
			elif item is 34:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/epgtranslator/epgtranslator.sh -qO - | /bin/sh"
        ])
			elif item is 35:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/feedsfinder/feedsfinder.sh -qO - | /bin/sh"
        ])
			elif item is 36:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/filecommander/filecommander.sh -qO - | /bin/sh"
        ])
			elif item is 37:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/filmxy/filmxy.sh -qO - | /bin/sh"
        ])
			elif item is 38:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/footonsat/footonsat.sh -qO - | /bin/sh"
        ])
			elif item is 39:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/footonsat-mohamed-os/footonsat_mohamed_os.sh -qO - | /bin/sh"
        ])
			elif item is 40:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/freearhey/freearhey.sh -qO - | /bin/sh"
        ])
			elif item is 41:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/freeserver/freeserver.sh -qO - | /bin/sh"
        ])
			elif item is 42:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/gioppygio/gioppygio.sh -qO - | /bin/sh"
        ])
			elif item is 43:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/hasbahca/hasbahca.sh -qO - | /bin/sh"
        ])
			elif item is 44:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/historyzapselector/historyzapselector-dorik.sh -qO - | /bin/sh"
        ])
			elif item is 45:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/horoscope/horoscope.sh -qO - | /bin/sh"
        ])
			elif item is 46:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/imdb/imdb.sh -qO - | /bin/sh"
        ])
			elif item is 47:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/internetspeedtest/internet-speed-test.sh -qO - | /bin/sh"
        ])
			elif item is 48:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/ipaudio/ipaudio.sh -qO - | /bin/sh"
        ])
			elif item is 49:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/ipaudio/ipaudio-7.4-ffmpeg.sh -qO - | /bin/sh"
        ])
			elif item is 50:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/ipaudiopro/1.3/ipaudiopro.sh -qO - | /bin/sh"
        ])
			elif item is 51:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/ipaudiopro/1.5/ipaudiopro.sh -qO - | /bin/sh"
        ])
			elif item is 52:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/ipchecker/ipchecker.sh -qO - | /bin/sh"
        ])
			elif item is 53:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/iptosat/iptosat.sh -qO - | /bin/sh"
        ])
			elif item is 54:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/iptvarchive/iptvarchive.sh -qO - | /bin/sh"
        ])
			elif item is 55:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/iptvdream-all/iptvdream-all.sh -qO - | /bin/sh"
        ])
			elif item is 56:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/isetting-e2/isetting-e2.sh -qO - | /bin/sh"
        ])
			elif item is 57:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/jediepgxtream/jediepgxtream.sh -qO - | /bin/sh"
        ])
			elif item is 58:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/jedimakerxtream/jedimakerxtream.sh -qO - | /bin/sh"
        ])
			elif item is 59:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/keyadder/keyadder.sh -qO - | /bin/sh"
        ])
			elif item is 60:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/lamedbmerger/lamedbmerger.sh -qO - | /bin/sh"
        ])
			elif item is 61:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/mmpicons/mmpicons.sh -qO - | /bin/sh"
        ])
			elif item is 62:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/moviebrowser/moviebrowser.sh -qO - | /bin/sh"
        ])
			elif item is 63:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/moviesmanager/moviesmanager.sh -qO - | /bin/sh"
        ])
			elif item is 64:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/multiquickbutton/multiquickbutton.sh -qO - | /bin/sh"
        ])
			elif item is 65:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/multistalker/multistalker.sh -qO - | /bin/sh"
        ])
			elif item is 66:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/multistalker-pro/multistalkerpro.sh -qO - | /bin/sh"
        ])
			elif item is 67:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/multistalker-pro/multi-stalkerpro.sh -qO - | /bin/sh"
        ])
			elif item is 68:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/mycam/mycam.sh -qO - | /bin/sh"
        ])
			elif item is 69:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/ncam-status/ncam-status.sh -qO - | /bin/sh"
        ])
			elif item is 70:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/newpermanentclock/newpermanentclock.sh -qO - | /bin/sh"
        ])
			elif item is 71:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/oaweather/oaweather.sh -qO - | /bin/sh"
        ])
			elif item is 72:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/oscam-status/oscam-status.sh -qO - | /bin/sh"
        ])
			elif item is 73:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/piconinstaller/piconinstaller.sh -qO - | /bin/sh"
        ])
			elif item is 74:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/pluginskinmover/pluginskinmover.sh -qO - | /bin/sh"
        ])
			elif item is 75:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/plutotv/plutotv.sh -qO - | /bin/sh"
        ])
			elif item is 76:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/quarter-pounder/quarter-pounder.sh -qO - | /bin/sh"
        ])
			elif item is 77:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/quran-karim/quran-karim.sh -qO - | /bin/sh"
        ])
			elif item is 78:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/quran/quran.sh -qO - | /bin/sh"
        ])
			elif item is 79:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/radiom/radiom.sh -qO - | /bin/sh"
        ])
			elif item is 80:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/radiogit/radiogit.sh -qO - | /bin/sh"
        ])
			elif item is 81:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/raedquicksignal/raedquicksignal.sh -qO - | /bin/sh"
        ])
			elif item is 82:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/rakutentv/rakutentv.sh -qO - | /bin/sh"
        ])
			elif item is 83:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/samsungtvplus/samsungtvplus.sh -qO - | /bin/sh"
        ])
			elif item is 84:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/screengrabber/screengrabber.sh -qO - | /bin/sh"
        ])
			elif item is 85:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/screennames/screennames.sh -qO - | /bin/sh"
        ])
			elif item is 86:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/scriptexecuter/scriptexecuter.sh -qO - | /bin/sh"
        ])
			elif item is 87:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/sherlockmod/sherlockmod.sh -qO - | /bin/sh"
        ])
			elif item is 88:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/shootyourscreen/shootyourscreen.sh -qO - | /bin/sh"
        ])
			elif item is 98:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/spinnerselector/spinnerselector.sh -qO - | /bin/sh"
        ])
			elif item is 90:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/subssupport/subssupport-1.5.8-r9.sh -qO - | /bin/sh"
        ])
			elif item is 91:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/subssupport/subssupport.sh -qO - | /bin/sh"
        ])
			elif item is 92:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/theweather/theweather.sh -qO - | /bin/sh"
        ])
			elif item is 93:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/tmdb/tmbd.sh -qO - | /bin/sh"
        ])
			elif item is 94:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/transmission/transmission.sh -qO - | /bin/sh"
        ])
			elif item is 95:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/vavoo/vavoo.sh -qO - | /bin/sh"
        ])
			elif item is 96:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/visualweather/visualweather.sh -qO - | /bin/sh"
        ])
			elif item is 97:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/weathermsn/weathermsn.sh -qO - | /bin/sh"
        ])
			elif item is 98:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/weatherplugin/weatherplugin.sh -qO - | /bin/sh"
        ])
			elif item is 99:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/weatherplugin-icons/weatherplugin-icons.sh -qO - | /bin/sh"
        ])
			elif item is 100:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/wireguard-vpn/wireguard-vpn.sh -qO - | /bin/sh"
        ])
			elif item is 101:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/worldcam/worldcam.sh -qO - | /bin/sh"
        ])
			elif item is 102:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/xcplugin-forever/xcplugin-forever.sh -qO - | /bin/sh"
        ])
			elif item is 103:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/xklass/xklass.sh -qO - | /bin/sh"
        ])
			elif item is 104:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/xstreamity/xstreamity.sh -qO - | /bin/sh"
        ])
			elif item is 105:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/xtraevent/xtraevent-4.2.sh -qO - | /bin/sh"
        ])
			elif item is 106:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/xtraevent/xtraevent-4.5.sh -qO - | /bin/sh"
        ])
			elif item is 107:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/xtraevent/new/xtraevent.sh -qO - | /bin/sh"
        ])
			elif item is 108:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/youtube/youtube.sh -qO - | /bin/sh"
        ])
			elif item is 109:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/foreca/foreca.sh -qO - | /bin/sh"
        ])
			elif item is 110:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/skine2sentials/skin-e2sentials.sh -qO - | /bin/sh"
        ])
			elif item is 111:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/hardwareinfo/hardwareinfo.sh -qO - | /bin/sh"
        ])
			elif item is 112:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/zaptimer/zaptimer.sh -qO - | /bin/sh"
        ])

			elif item is 113:
				self.session.open(Console, _("Installing package please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/extensions/-/raw/main/e2reader/enigma2readeradder.sh -qO - | /bin/sh"
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
