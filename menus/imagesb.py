from Plugins.Extensions.ElieSatPanel.__init__  import Version, Panel
from Tools.Directories import fileExists, resolveFilename, SCOPE_PLUGINS
from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.MenuList import MenuList
from Components.Button import Button
from Components.Pixmap import Pixmap
from enigma import eConsoleAppContainer
from enigma import eTimer
import urllib.request
import json
import os
import logging
import re
import shutil
import glob

PLUGINS = {
    "Bitrate": "opkg install enigma2-plugin-extensions-bitrate", 
    "Cacheflush": "opkg install enigma2-plugin-extensions-cacheflush",  
    "Chocholousek-picons": "opkg install enigma2-plugin-extensions-chocholousek-picons",
    "E2iplayer-deps": "opkg install enigma2-plugin-extensions-e2iplayer-deps ", 
    "Epgimport": "opkg install enigma2-plugin-extensions-epgimport",
    "Epgtranslator": "opkg install enigma2-plugin-extensions-epgtranslator",
    "Ipchecker": "opkg install enigma2-plugin-extensions-ipchecker",
    "Oaweather": "opkg install enigma2-plugin-extensions-oaweather",
    "Permanentclock": "opkg install enigma2-plugin-extensions-permanentclock",
    "Setpicon": "opkg install enigma2-plugin-extensions-setpicon",
    "Tmdb": "opkg install enigma2-plugin-extensions-tmdb",
    "Autoresolution": "opkg install enigma2-plugin-systemplugins-autoresolution",
    "Weathercomponenthandler": "opkg install enigma2-plugin-systemplugins-weathercomponenthandler",
    "Ai-powered-subtitle-translation": "opkg install enigma2-plugin-subscription-ai-powered-subtitle-translation",
    "Metrix-atv-fhd-icons": "opkg install enigma2-plugin-skins-metrix-atv-fhd-icons",
}
FILE = "/usr/lib/enigma2/python/Plugins/Extensions/ElieSatPanel/menus/Imagesb"
DIR = "/usr/lib/enigma2/python/Plugins/Extensions/"

class imagesb(Screen):
    skin = """
<screen name="Backup" position="center,center" size="1920,1080" title="Backup">
        
<!-- menu -->
<widget name="menu" selectionPixmap="/usr/lib/enigma2/python/Plugins/Extensions/ElieSatPanel/images/selection.png"  position="48,200" size="1240,660" scrollbarMode="showOnDemand" itemHeight="66" font="Regular;35" transparent="1" />
<widget name="background" position="0,0" size="1920,1080" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ElieSatPanel/images/bglist.png" zPosition="-1" alphatest="on" />

<!-- title -->
<eLabel text="Packages:" position="160,105" size="400,50" zPosition="1" font="Regular;39" halign="left" backgroundColor="background" foregroundColor="foreground" transparent="1" />
<ePixmap position="73,105" size="180,47" zPosition="1" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ElieSatPanel/images/2.png" alphatest="blend" />
<eLabel text="Descriptions:" position="770,105" size="400,50" zPosition="1" font="Regular;39" halign="left" backgroundColor="background" foregroundColor="foreground" transparent="1" />
<ePixmap position="683,105" size="50,47" zPosition="1" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ElieSatPanel/images/2.png" alphatest="blend" />

<!-- title2 -->
<widget name="status" position="200,880" size="1240,50" zPosition="1" font="Regular;40" halign="left" backgroundColor="background" foregroundColor="foreground" transparent="1" />
<ePixmap position="110,880" size="180,47" zPosition="1" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ElieSatPanel/images/2.png" alphatest="blend" />
    <eLabel backgroundColor="#00ffffff" position="55,860" size="1220,1" zPosition="2" />
    <eLabel backgroundColor="#00ffffff" position="55,195" size="1220,1" zPosition="2" />
<eLabel text="ELIE" position="1450,535" size="400,50" zPosition="1" font="Regular;39" halign="left" backgroundColor="background" foregroundColor="foreground" transparent="1" />
<eLabel text="PANEL" position="1635,535" size="400,50" zPosition="1" font="Regular;39" halign="left" backgroundColor="background" foregroundColor="foreground" transparent="1" />
<widget name="Version" position="1510,650" size="150,50" font="Regular;35" halign="center" valign="center" backgroundColor="background" foregroundColor="foreground" transparent="1"/>
<ePixmap position="1525,505" size="240,150" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ElieSatPanel/images/icon.png" zPosition="2" alphatest="blend" />

<!-- clock -->
<widget source="global.CurrentTime" render="Label" position="1290,400" size="350,90" font="lsat; 75" noWrap="1" halign="center" valign="bottom" foregroundColor="#11ffffff" backgroundColor="#20000000" transparent="1" zPosition="2">
		<convert type="ClockToText">Default</convert>
<!-- calender -->
</widget>
<widget source="global.CurrentTime" render="Label" position="1530,410" size="335,54" font="lsat; 24" halign="center" valign="bottom" foregroundColor="#11ffffff" backgroundColor="#20000000" transparent="1" zPosition="1">
<convert type="ClockToText">Format %A %d %B</convert>
</widget>
<!-- minitv -->
<widget source="session.VideoPicture" render="Pig" position="1305,100" size="550,290" zPosition="1" backgroundColor="#ff000000" />

<!--buttons -->
<widget name="key_red" position="150,960"  size="165,45" font="Regular;35" halign="center" backgroundColor="background" foregroundColor="foreground" transparent="1" />
<ePixmap position="120,1015" zPosition="1" size="240,10" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ElieSatPanel/images/red.png" alphatest="blend" />
<widget name="key_green" position="430,960"  size="165,45" font="Regular;35" halign="center" backgroundColor="background" foregroundColor="foreground" transparent="1" />
<ePixmap position="400,1015" zPosition="1" size="240,10" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ElieSatPanel/images/green.png" alphatest="blend" />
<widget name="key_yellow" position="680,960"  size="250,45" font="Regular;35" halign="center" backgroundColor="background" foregroundColor="foreground" transparent="1" />
<ePixmap position="680,1015" zPosition="1" size="240,10" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ElieSatPanel/images/yellow.png" alphatest="blend" />
<widget name="key_blue" position="990,960"  size="165,45" font="Regular;35" halign="center" backgroundColor="background" foregroundColor="foreground" transparent="1" />
<ePixmap position="960,1015" zPosition="1" size="240,10" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ElieSatPanel/images/blue.png" alphatest="blend" />
</screen>
    """

    def __init__(self, session):
        self.session = session
        Screen.__init__(self, session)

        self.selected_plugins = set()
        self.plugin_display_list = [f"{plugin}" for plugin in PLUGINS.keys()]
        self.current_install_index = 0
        self.installed_plugins = set()

        self["Version"] = Label(_("V" + Version))
        self["menu"] = MenuList(self.plugin_display_list)
        self["background"] = Pixmap()
        self["status"] = Label("Select plugins with OK, install with Green")
        self["key_green"] = Button("Install")
        self["key_red"] = Button("Restart")
        self["key_yellow"] = Button("Dependencies")
        self["key_blue"] = Button("Report")

        self["actions"] = ActionMap(
            ["ColorActions", "SetupActions"],
            {
                "green": self.start_installation,
                "red": self.restart_enigma2,
                "blue": self.report,
                "ok": self.toggle_selection,
                "cancel": self.close,
            },
        )

        self.container = eConsoleAppContainer()
        self.container.appClosed.append(self.command_finished)
        self.update_status()

    def toggle_selection(self):
        current_index = self["menu"].getSelectionIndex()
        current_plugin = list(PLUGINS.keys())[current_index]

        if current_plugin in self.selected_plugins:
            self.selected_plugins.remove(current_plugin)
            self.plugin_display_list[current_index] = f" {current_plugin}"
            self.remove_plugin_from_file(current_plugin)
        else:
            self.selected_plugins.add(current_plugin)
            self.plugin_display_list[current_index] = f"Ready to install  {current_plugin}"
            self.log_selected_plugin(current_plugin)

        self["menu"].setList(self.plugin_display_list)
        self.update_status()

    def update_status(self):
        count = len(self.selected_plugins)
        if count == 0:
            self["status"].setText("Select with ok and press the green button to install")
        elif count == 1:
            self["status"].setText("1 package selected")
        else:
            self["status"].setText(f"{count} packages selected")

    def log_selected_plugin(self, plugin):
        try:
            logging.debug(f"Logging selected plugin: {plugin}")
            plugin_dir = os.path.dirname(FILE)
            if not os.path.exists(plugin_dir):
                os.makedirs(plugin_dir)
                logging.debug(f"Created directory: {plugin_dir}")

            existing_plugins = set()
            if os.path.exists(FILE):
                with open(FILE, "r") as f:
                    existing_plugins = {line.strip() for line in f if line.strip()}
                logging.debug(f"Existing plugins in file: {existing_plugins}")

            if plugin not in existing_plugins:
                with open(FILE, "a") as f:
                    f.write(f"{plugin}\n")
                logging.debug(f"Successfully logged plugin {plugin} to {FILE}")
            else:
                logging.debug(f"Plugin {plugin} already exists in {FILE}")

        except Exception as e:
            logging.error(f"Error logging plugin {plugin} to {FILE}: {str(e)}")
            self["status"].setText(f"Error logging plugin {plugin}: {str(e)}")

    def remove_plugin_from_file(self, plugin):
        try:
            if os.path.exists(FILE):
                with open(FILE, "r") as f:
                    plugins = [line.strip() for line in f if line.strip()]
                plugins = [p for p in plugins if p != plugin]
                with open(FILE, "w") as f:
                    for p in plugins:
                        f.write(f"{p}\n")
                logging.debug(f"Removed plugin {plugin} from {FILE}")
        except Exception as e:
            logging.error(f"Error removing plugin {plugin} from {FILE}: {str(e)}")
            self["status"].setText(f"Error removing plugin {plugin}: {str(e)}")
    def find_plugin_folder(self, plugin_name):
        if not os.path.exists(DIR):
            return None

        PLUGIN_FOLDER_MAP = {
            "Levi45 Addons Manager": "Levi45Addons",
            "TV Addon": "tvaddon",
            "SubsSupport 1.7.0-r18 Mnasr": "SubsSupport",
        }
        if plugin_name in PLUGIN_FOLDER_MAP:
            folder = PLUGIN_FOLDER_MAP[plugin_name]
            if os.path.exists(os.path.join(DIR, folder)):
                return folder

        normalized_name = re.sub(r'[\s\-\_]', '', plugin_name.lower())
        normalized_name = re.sub(r'\d+\.\d+\.\d+.*|r\d+', '', normalized_name)
        for folder in os.listdir(DIR):
            normalized_folder = re.sub(r'[\s\-\_]', '', folder.lower())
            if normalized_folder == normalized_name or folder.lower() == plugin_name.lower():
                return folder
        return None

    def start_installation(self):
        if not self.selected_plugins:
            self["status"].setText("No plugins selected!")
            return

        self.plugins_to_install = list(self.selected_plugins)
        self.current_install_index = 0
        self.installed_plugins.clear()
        self.install_next_plugin()

    def install_next_plugin(self):
        logging.debug(f"Installing plugin {self.current_install_index + 1}/{len(self.plugins_to_install)}")
        if self.current_install_index >= len(self.plugins_to_install):
            self["status"].setText("All installations complete!")
            logging.debug(f"All installations complete, installed_plugins: {self.installed_plugins}")
            self.clear_selections()
            return

        plugin = self.plugins_to_install[self.current_install_index]
        self["status"].setText(f"Installing {plugin} ({self.current_install_index + 1}/{len(self.plugins_to_install)})...")
        logging.debug(f"Executing command for plugin: {plugin}")
        self.container.execute(PLUGINS[plugin])

    def command_finished(self, retval):
        current_plugin = self.plugins_to_install[self.current_install_index]
        logging.debug(f"Installation finished for plugin {current_plugin}, return value: {retval}")
        folder_name = self.find_plugin_folder(current_plugin)
        package_installed = False

        if folder_name:
            if os.system(f"opkg list-installed | grep -q enigma2-plugin-extensions-{folder_name.lower()}") == 0:
                package_installed = True
            elif os.system(f"dpkg -l | grep -q enigma2-plugin-extensions-{folder_name.lower()}") == 0:
                package_installed = True

        if retval == 0 and (folder_name or package_installed):
            logging.debug(f"Plugin {current_plugin} successfully installed in folder {folder_name or 'unknown'}")
            self.installed_plugins.add(current_plugin)
            self.current_install_index += 1
            self.install_next_plugin()
        else:
            logging.warning(f"Plugin {current_plugin} not found in {DIR} or not installed, retval: {retval}")
            self["status"].setText(f"Plugin {current_plugin} not installed properly!")
            self.remove_plugin_from_file(current_plugin)
            self.current_install_index += 1
            self.install_next_plugin()

    def clear_selections(self):
        self.selected_plugins.clear()
        self.plugin_display_list = [f"{plugin}" for plugin in PLUGINS.keys()]
        self["menu"].setList(self.plugin_display_list)
        self.update_status()

    def restart_enigma2(self):
        self.container.execute("init 4 && init 3")
        self.close()

    def report(self):
        info_path = resolveFilename(SCOPE_PLUGINS, "Extensions/ElieSatPanel/menus/Imagesb")
        if fileExists(info_path):
            try:
                with open(info_path, "r") as f:
                    content = f.read()
                self.session.open(MessageBox, content, MessageBox.TYPE_INFO)
            except Exception as e:
                self.session.open(MessageBox, f"Error reading report file: {str(e)}", MessageBox.TYPE_ERROR)
        else:
            self.session.open(MessageBox, "report file not found", MessageBox.TYPE_ERROR)
