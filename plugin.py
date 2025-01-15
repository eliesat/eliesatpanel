from Plugins.Plugin import PluginDescriptor
from Screens.MessageBox import MessageBox
from enigma import  getDesktop
from .mainmenu import eliesatpanel

def isHD():
	if getDesktop(0).size().width() < 1920:
		return True
	else:
		return False

def main(session, **kwargs):
    if isHD():
        session.open(MessageBox, _('Install a fhd skin and try again...'), MessageBox.TYPE_ERROR)
    else:
        session.open(eliesatpanel)

def Plugins(**kwargs):
    return [
        PluginDescriptor(
            name="ElieSatPanel",
            description=f"Addons for enigma2 devices",
            where=PluginDescriptor.WHERE_PLUGINMENU,
            icon="esp.png",
            fnc=main,
        )
    ]
