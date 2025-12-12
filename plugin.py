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
        session.open(MessageBox, _('Install a FHD skin and try again...'), MessageBox.TYPE_ERROR)
    else:
        message_text = _(
            "إعلان هام.\n\n"
            "نود إعلامكم بأنه سيتم إيقاف دعم وتحديثات البانل بشكل نهائي ابتداءً من بداية السنة القادمة ٢٠٢٦.\n\n"
            "سيستمر البانل بالعمل كما هو، ولكن لن يتم إصدار تحديثات أو توفير دعم تقني بعد هذا التاريخ. نشكر جميع المستخدمين على ثقتهم ودعمهم خلال الفترة الماضية.\n\n"
"النسخة الجديدة مخصصة للمشتركين عن طريقي باحد خدمات الا بي تي في للحصول عليها:\n"
            "التواصل عبر واتساب على الرقم: 70787872 961\n"
 "مع التحية والتقدير.\n"
"فريق التطوير"
        )

        # Show multi-line message in MessageBox; scroll automatically if too long
        session.openWithCallback(
            lambda result: open_panel(session, result),
            MessageBox,
            message_text,
            MessageBox.TYPE_INFO
        )

# Callback function to open the plugin after user presses OK
def open_panel(session, result):
    if result is None or result:
        session.open(eliesatpanel)

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

