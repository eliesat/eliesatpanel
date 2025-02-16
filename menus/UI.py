from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Screens.Standby import TryQuitMainloop
from Screens.Console import Console
from Components.Sources.StaticText import StaticText
from Components.config import config
from Components.ConfigList import ConfigListScreen
from Components.Pixmap import Pixmap
from Components.ActionMap import ActionMap, NumberActionMap
from Components.Sources.List import List
from Components.Console import Console as iConsole
from Components.Label import Label
from Components.MenuList import MenuList
from Plugins.Plugin import PluginDescriptor
from Components.Language import language
from Tools.LoadPixmap import LoadPixmap
from Tools.Directories import fileExists, pathExists, resolveFilename, SCOPE_PLUGINS, SCOPE_LANGUAGE
from os import environ
import os
import glob
import gettext
import time

def status_path():
	status = '/usr/lib/opkg/status'
	if fileExists("/usr/lib/ipkg/status"):
		status = "/usr/lib/ipkg/status"
	elif fileExists("/var/lib/opkg/status"):
		status = "/var/lib/opkg/status"
	elif fileExists("/var/opkg/status"):
		status = "/var/opkg/status"
	return status

lang = language.getLanguage()
environ["LANGUAGE"] = lang[:2]
gettext.bindtextdomain("enigma2", resolveFilename(SCOPE_LANGUAGE))
gettext.textdomain("enigma2")
gettext.bindtextdomain("epanel", "%s%s" % (resolveFilename(SCOPE_PLUGINS), "Extensions/epanel/locale/"))

def _(txt):
	t = gettext.dgettext("epanel", txt)
	if t == txt:
		t = gettext.gettext(txt)
	return t
	
class ui(Screen):
	skin = """
<screen name="uninstall" position="0,0" size="1920,1080" backgroundColor="transparent" flags="wfNoBorder" title="ElieSatPanel">
<ePixmap position="0,0" zPosition="-1" size="1920,1080" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ElieSatPanel/images/bglist.png"/>
<widget source="menu" selectionPixmap="/usr/lib/enigma2/python/Plugins/Extensions/ElieSatPanel/images/selection.png" render="Listbox" position="48,200" size="1240,660"  transparent="1">
	<convert type="TemplatedMultiContent">
		{"template": [
			MultiContentEntryText(pos = (120, 10), size = (900, 45), font=0, flags = RT_HALIGN_LEFT, text = 0), # index 2 is the Menu Titel
			MultiContentEntryText(pos = (1030, 19), size = (900, 35), font=1, flags = RT_HALIGN_LEFT, text = 1), # index 3 is the Description
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

	def finish(self, result, retval, extra_args):
		self.nList()

