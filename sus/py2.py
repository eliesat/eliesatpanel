import os
from Plugins.Extensions.ElieSatPanel.menus.Console import Console
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Components.ActionMap import ActionMap
from Components.ConfigList import ConfigListScreen
from Components.config import ConfigText, ConfigInteger, getConfigListEntry
from Components.Console import Console
from Plugins.Plugin import PluginDescriptor
from Plugins.Extensions.ElieSatPanel.menus.Console import Console
class iptv2(Screen, ConfigListScreen):
    skin = """
<screen name="iptv" position="0,0" size="1920,1080" backgroundColor="transparent" flags="wfNoBorder" title="iptvadder">
<ePixmap position="0,0" zPosition="-1" size="1920,1080" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ElieSatPanel/images/bglist.png"/>
<widget name="config" position="48,200" size="1240,660" font="Regular;35" halign="center" valign="center" render="Listbox" itemHeight="66" selectionPixmap="/usr/lib/enigma2/python/Plugins/Extensions/ElieSatPanel/images/selection.png" transparent="1" scrollbarMode="showOnDemand" />

<eLabel text="Iptv user adder" position="460,120" size="400,50" zPosition="1" font="Regular;39" halign="left" backgroundColor="background" foregroundColor="foreground" transparent="1" />
<ePixmap position="370,125" size="180,47" zPosition="1" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ElieSatPanel/images/2.png" alphatest="blend" />
<ePixmap position="780,125" size="180,47" zPosition="1" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ElieSatPanel/images/2.png" alphatest="blend" />
<!-- title2 -->
<eLabel text="Select and press ok to write on the screen" position="280,880" size="1000,50" zPosition="1" font="Regular;40" halign="left" backgroundColor="background" foregroundColor="foreground" transparent="1" />
<ePixmap position="210,880" size="180,47" zPosition="1" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ElieSatPanel/images/2.png" alphatest="blend" />

<ePixmap position="120,1015" zPosition="1" size="240,10" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ElieSatPanel/images/red.png" alphatest="blend" />            
<eLabel text="Close" position="160,960" zPosition="2" size="165,45" font="Regular;35" halign="center" valign="center" backgroundColor="background" foregroundColor="foreground" transparent="1" />     
<ePixmap position="400,1015" zPosition="1" size="240,10" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ElieSatPanel/images/green.png" alphatest="blend" />
<eLabel text="Send" position="387.5,960" zPosition="2" size="265,45" font="Regular;35" halign="center" valign="center" backgroundColor="background" foregroundColor="foreground" transparent="1" />
<ePixmap position="680,1015" zPosition="1" size="240,10" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ElieSatPanel/images/yellow.png" alphatest="blend" />
<eLabel text="Save" position="720,960" zPosition="2" size="165,45" font="Regular;35" halign="center" valign="center" backgroundColor="background" foregroundColor="foreground" transparent="1" />
<ePixmap position="960,1015" zPosition="1" size="240,10" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ElieSatPanel/images/blue.png" alphatest="blend" />
<eLabel text="CheckUser" position="985,960" zPosition="2" size="185,45" font="Regular;35" halign="center" valign="center" backgroundColor="background" foregroundColor="foreground" transparent="1" />
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

    <eLabel backgroundColor="#00ffffff" position="55,860" size="1220,3" zPosition="2" />
    <eLabel backgroundColor="#00ffffff" position="55,195" size="1220,3" zPosition="2" />
        </screen>
    """

    def __init__(self, session):
        self.session = session
        Screen.__init__(self, session)
        self["actions"] = ActionMap(["SetupActions", "ColorActions"], {
            "cancel": self.exit,
            "red": self.exit,
            "green": self.send,
            "yellow": self.save,
            "blue": self.check
        }, -2)

        self.url = ConfigText(default="http://eliesatpanel.com", fixed_size=False)
        self.port = ConfigText(default="8080", fixed_size=False)
        self.user = ConfigText(default="username", fixed_size=False)
        self.passw = ConfigText(default="password", fixed_size=False)

        ConfigListScreen.__init__(self, [
            getConfigListEntry("URL :", self.url),
            getConfigListEntry("PORT :", self.port),
            getConfigListEntry("USERNAME :", self.user),
            getConfigListEntry("PASSWORD :", self.passw),
        ])

    def exit(self):
        self.close()

    def send(self):
     cmd1 = ". /usr/lib/enigma2/python/Plugins/Extensions/ElieSatPanel/sus/iptv.sh"
     self.session.open(Console, _("Writing your iptv suscription, please wait"), cmdlist=[cmd1])

    def save(self):
        line = {
            "url": self.url.value,
            "port": self.port.value,
            "user": self.user.value,
            "passw": self.passw.value
        }
        self.writeConfigFile(line, ".m3u")
        self.session.open(MessageBox, "Iptv new user is saved successfully, press the green button to add in playlists", MessageBox.TYPE_INFO, timeout=10)
    def writeConfigFile(self, line, extension):
        config_file = {
            ".m3u": [
                "/usr/lib/enigma2/python/Plugins/Extensions/ElieSatPanel/sus/iptv.txt",
            ],
        }

        for path in config_file[extension]:
            if extension == ".m3u":
                    sus = "{url} {port} {user} {passw}\n".format(**line)
            with open(path, "a") as f:
                f.write(sus)


    def check(self):
        self.close()
    def exit(self):
        self.close()
