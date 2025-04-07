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
from Plugins.Extensions.ElieSatPanel.menus.compat import compat_urlopen, compat_Request, PY3, readFromFile
from Plugins.Extensions.ElieSatPanel.menus.Console import Console
from Plugins.Extensions.ElieSatPanel.__init__  import Version, Panel
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
installer = 'https://raw.githubusercontent.com/eliesat/eliesatpanel/main/installer.sh'
scriptpath = "/usr/script/"

class piconsmain(Screen):
	def __init__(self, session):
		self.session = session
		Screen.__init__(self, session)
		skin = "/skins/submenus-fhd.xml"
		self.skin = readFromFile(skin)
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
			"info": self.infoKey,
		})
		self.list = []
		self["menu"] = List(self.list)
		self.mList()
		self["MemoryLabel"] = StaticText(_("Ram:"))
		self["SwapLabel"] = StaticText(_("Swap:"))
		self["FlashLabel"] = StaticText(_("Flash:"))
		self["gstreamerLabel"] = StaticText(_("Gst:"))
		self["pythonLabel"] = StaticText(_("Py:"))
		self["CPULabel"] = StaticText(_("Prc:"))
		self["HardwareLabel"] = StaticText(_("Hdw:"))
		self["ImageLabel"] = StaticText(_("Img:"))
		self["KernelLabel"] = StaticText(_("Krn:"))
		self["EnigmaVersionLabel"] = StaticText(_("Upd:"))
		self["driverLabel"] = StaticText(_("Drv:"))
		self["ipLabel"] = StaticText(_("IP address:"))
		self["macLabel"] = StaticText(_("Mac Address:"))
		self["internetLabel"] = StaticText(_("Internet:"))
		self["memTotal"] = StaticText()
		self["swapTotal"] = StaticText()
		self["flashTotal"] = StaticText()
		self["device"] = StaticText()
		self["gstreamer"] = StaticText()
		self["python"] = StaticText()
		self["Hardware"] = StaticText()
		self["Image"] = StaticText()
		self["CPU"] = StaticText()
		self["Kernel"] = StaticText()
		self["ipInfo"] = StaticText()
		self["macInfo"] = StaticText()
		self["EnigmaVersion"] = StaticText()
		self["driver"] = StaticText()
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
		self["internet"] = StaticText()
		self.intInfo()
		t = Timer(0.5, self.update_picons)
		t.start()

	def mList(self):
		self.list = []
		a = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/images/1.png"))

		self.list.append((_("Picons-Snp"), 1, _("بيكونات بحسب اسم القناة"), a))
		self.list.append((_("Picons-Srp"), 2, _("بيكونات بحسب ريفيرانس القناة"), a))
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
				self.session.open(snp)
			elif item is 2:
				self.session.open(srp)
			else:
				self.close(None)

	def keyNumberGlobal(self, number):
			print('pressed', number)
			if number == 0:
				self.session.open(Console, _("Updating ElieSatPanel, please wait..."), [
            "wget --no-check-certificate https://raw.githubusercontent.com/eliesat/eliesatpanel/main/installer.sh -qO - | /bin/sh"
        ])
			else:
				return

	def exit(self):
		self.close()

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

	def update_picons(self):
		import requests
		url = 'https://raw.githubusercontent.com/eliesat/eliesatpanel/refs/heads/main/sub/picons'
		response = requests.get(url)
		file_Path = '/usr/lib/enigma2/python/Plugins/Extensions/ElieSatPanel/sub/picons'
		if response.status_code == 200:
			with open(file_Path, 'wb') as file:
				file.write(response.content)
			print('File downloaded successfully')
		else:
			print('Failed to download file')

		
	def cancel(self):
		self.close()


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


def status_path():
	if fileExists("/usr/lib/enigma2/python/Plugins/Extensions/ElieSatPanel/sub/picons"):
		status = "/usr/lib/enigma2/python/Plugins/Extensions/ElieSatPanel/sub/picons"
	return status

#############################################################################
class snp(Screen):
	def __init__(self, session, args=None):
		Screen.__init__(self, session)
		skin = "/skins/addons-fhd.xml"
		self.skin = readFromFile(skin)
		self.setTitle(_("Ipk remove"))
		self.session = session
		self.path = status_path()
		self.iConsole = iConsole()
		self.status = False
		self["key_red"] = StaticText(_("Close"))
		self["key_green"] = StaticText(_("Install"))
		self["key_yellow"] = StaticText(_("Browse"))
		self["key_blue"] = StaticText(_("RestartE2"))
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
		self["Panel"] = Label(_(Panel))
		self["Version"] = Label(_("V" + Version))
		self["shortcuts"] = NumberActionMap(["ShortcutActions", "WizardActions",  "ColorActions", "HotkeyActions"],
		{
				"cancel": self.cancel,
				"back": self.cancel,
				"ok": self.install,
				"red": self.cancel,
				"green": self.install,
				"yellow": self.browse,
				"blue": self.restart,
				"info": self.infoKey,
			},-1)
		
	def nList(self):
		self.list = []
		ipkminipng = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/images/1.png"))
		for line in open(status_path()):
			if "Package:" in line:
				name1 = line.replace("\n","").split()[-1]
			elif "Version:" in line:
				name2 = line.replace("\n","").split(r"(\s+)")[-1]
			elif "Status:" in line and "Snp" in line:
				self.list.append((name1, name2, ipkminipng))
		self.list.sort()
		self["menu"].setList(self.list)

	def install(self):
		pkg_name = self["menu"].getCurrent()[0]
		for line in open(status_path()):
				if line.startswith(pkg_name):
					remote_changelog = line.split("=")
					remote_changelog = line.split("'")[1]
					wget = 'wget --no-check-certificate'
					Installer = remote_changelog
					runbs = '-qO - | /bin/sh'
					self.session.open(Console, _("Running the script, please wait..."), [
         ("%s %s %s" % (wget, Installer, runbs))
        ])

	def cancel(self):
		self.close()

	def restart (self):
				self.session.open(Console, _("Restarting enigma2 please wait..."), [
            "[ command -v dpkg &> /dev/null ] && systemctl restart enigma2 || killall -9 enigma2"
        ])
	def browse(self):
		self.session.open(PluginBrowser)

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
	def finish(self, result, retval, extra_args):
		self.nList()
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
	def infoKey (self):
		self.session.open(Console, _("Please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/scripts/-/raw/main/check/_check-all.sh -qO - | /bin/sh"
        ])

#############################################################################
class srp(Screen):
	def __init__(self, session, args=None):
		Screen.__init__(self, session)
		skin = "/skins/addons-fhd.xml"
		self.skin = readFromFile(skin)
		self.setTitle(_("Ipk remove"))
		self.session = session
		self.path = status_path()
		self.iConsole = iConsole()
		self.status = False
		self["key_red"] = StaticText(_("Close"))
		self["key_green"] = StaticText(_("Install"))
		self["key_yellow"] = StaticText(_("Browse"))
		self["key_blue"] = StaticText(_("RestartE2"))
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
		self["Panel"] = Label(_(Panel))
		self["Version"] = Label(_("V" + Version))
		self["shortcuts"] = NumberActionMap(["ShortcutActions", "WizardActions",  "ColorActions", "HotkeyActions"],
		{
				"cancel": self.cancel,
				"back": self.cancel,
				"ok": self.install,
				"red": self.cancel,
				"green": self.install,
				"yellow": self.browse,
				"blue": self.restart,
				"info": self.infoKey,
			},-1)
		
	def nList(self):
		self.list = []
		ipkminipng = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/images/1.png"))
		for line in open(status_path()):
			if "Package:" in line:
				name1 = line.replace("\n","").split()[-1]
			elif "Version:" in line:
				name2 = line.replace("\n","").split(r"(\s+)")[-1]
			elif "Status:" in line and "Srp" in line:
				self.list.append((name1, name2, ipkminipng))
		self.list.sort()
		self["menu"].setList(self.list)

	def install(self):
		pkg_name = self["menu"].getCurrent()[0]
		for line in open(status_path()):
				if line.startswith(pkg_name):
					remote_changelog = line.split("=")
					remote_changelog = line.split("'")[1]
					wget = 'wget --no-check-certificate'
					Installer = remote_changelog
					runbs = '-qO - | /bin/sh'
					self.session.open(Console, _("Running the script, please wait..."), [
         ("%s %s %s" % (wget, Installer, runbs))
        ])

	def cancel(self):
		self.close()

	def restart (self):
				self.session.open(Console, _("Restarting enigma2 please wait..."), [
            "[ command -v dpkg &> /dev/null ] && systemctl restart enigma2 || killall -9 enigma2"
        ])
	def browse(self):
		self.session.open(PluginBrowser)

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
	def finish(self, result, retval, extra_args):
		self.nList()
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
	def infoKey (self):
		self.session.open(Console, _("Please wait..."), [
            "wget --no-check-certificate https://gitlab.com/eliesat/scripts/-/raw/main/check/_check-all.sh -qO - | /bin/sh"
        ])

#############################################################################
