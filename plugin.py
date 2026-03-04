# -*- coding: utf-8 -*-

from Plugins.Plugin import PluginDescriptor
from Screens.MessageBox import MessageBox
from enigma import getDesktop
from .mainmenu import eliesatpanel

# Check if the screen is HD
def isHD():
    return getDesktop(0).size().width() < 1920

# Main entry point for the plugin
def main(session, **kwargs):
    if isHD():
        session.open(
            MessageBox,
            _('Install a FHD skin and try again...'),
            MessageBox.TYPE_ERROR
        )
    else:
        message_text = _(
            "● This is an outdated version.\n"
            "Please contact technical support for the latest release. (961 70787872)\n"
            "----------------------------------\n"
            "\n"
            "إعلان هام\n\n"
            "● هذه نسخة قديمة. يرجى الاتصال بالدعم الفني للحصول على أحدث إصدار.\n"
            "- للتواصل عبر الواتساب على الرقم:  96170787872+\n"
            "مع التحية والتقدير، فريق التطوير"
        )

        # Show message only — DO NOT open panel after OK
        session.open(
            MessageBox,
            message_text,
            MessageBox.TYPE_INFO
        )

# Menu entry for the plugin
def menu(menuid, **kwargs):
    if menuid == "mainmenu":
        return [(_("ElieSatPanel"), main, _("eliesatpanel_"), 48)]
    return []

# Register the plugin in Enigma2
def Plugins(**kwargs):
    return [
        PluginDescriptor(
            name="ElieSatPanel",
            description=_("Addons for enigma2 devices"),
            where=PluginDescriptor.WHERE_PLUGINMENU,
            icon="esp.png",
            fnc=main
        ),
        PluginDescriptor(
            name="ElieSatPanel",
            description=_("Addons for enigma2 devices"),
            where=PluginDescriptor.WHERE_MENU,
            fnc=menu
        )
    ]
