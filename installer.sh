#!/bin/bash

clear >/dev/null 2>&1
# Check script url connectivity and install eliesatpanel
#######################################
if wget -q --method=HEAD https://github.com/eliesat/eliesatpanel/blob/main/installer.sh; then
connection=ok
else
echo "> Server is down, try again later..."
exit 1
fi
###########################################
version='3.1'
changelog='\panel update'

# Functions
###########################################
print_message() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}
print_message "> Start of process ..."
echo "-----------------------------------------------"
echo
sleep 2

cleanup() {
    rm -rf /var/cache/opkg/* /var/lib/opkg/lists/* /run/opkg.lock $i >/dev/null 2>&1
}
###########################################
image_version="/etc/image-version"
box_type=$(head -n 1 /etc/hostname)
distro_value=$(grep '^distro=' "$image_version" | awk -F '=' '{print $2}')
distro_version=$(grep '^version=' "$image_version" | awk -F '=' '{print $2}')
python_version=$(python --version 2>&1 | sed 's/[^ ]* //')

print_message "> Image : $distro_value-$distro_version"
sleep 2
print_message "> Python : $python_version"
sleep 2

# check libraries
###########################################
if [ -f /var/lib/dpkg/status ]; then
   STATUS=/var/lib/dpkg/status
   OSTYPE=DreamOs
else
   STATUS=/var/lib/opkg/status
   OSTYPE=Dream
fi
echo ""
if python --version 2>&1 | grep -q '^Python 3\.'; then
	PYTHON=PY3
	Packagesix=python3-six
	Packagerequests=python3-requests
else
	PYTHON=PY2
	Packagerequests=python-requests
fi

if [ $PYTHON = "PY3" ]; then
	if grep -qs "Package: $Packagesix" cat $STATUS ; then
		ok=ok
	else
		opkg update && opkg install python3-six >/dev/null 2>&1
	fi
fi
if grep -qs "Package: $Packagerequests" cat $STATUS ; then
	ok=ok
else
	if [ $OSTYPE = "DreamOs" ]; then
		apt-get update && apt-get install python-requests -y >/dev/null 2>&1
	elif [ $PYTHON = "PY3" ]; then
		opkg update >/dev/null 2>&1 && opkg install python3-requests >/dev/null 2>&1
	elif [ $PYTHON = "PY2" ]; then
		opkg update >/dev/null 2>&1 && opkg install python-requests >/dev/null 2>&1
	fi
fi

#configuration
###########################################
plugin=main
url=https://github.com/eliesat/eliesatpanel/archive/main.tar.gz
package=/tmp/$plugin.tar.gz
rm -rf /tmp/$plugin.tar.gz >/dev/null 2>&1

# Remove unnecessary files and folders
###########################################
[ -d "/CONTROL" ] && rm -r /CONTROL >/dev/null 2>&1
rm -rf /control /postinst /preinst /prerm /postrm /tmp/*.ipk /tmp/*.tar.gz >/dev/null 2>&1

# Download and install eliesatpanel
#######################################

wget -qO $package --no-check-certificate $url
tar -xzf $package -C /tmp
extract=$?
rm -rf $package >/dev/null 2>&1

if [ $extract -eq 0 ]; then
    rm -rf /usr/lib/enigma2/python/Plugins/Extensions/ElieSatPanel >/dev/null 2>&1
    mkdir -p /usr/lib/enigma2/python/Plugins/Extensions/ElieSatPanel
    create=$?
    if [ $create -eq 0 ]; then
    mv /tmp/eliesatpanel-main/* /usr/lib/enigma2/python/Plugins/Extensions/ElieSatPanel/ >/dev/null 2>&1
    rm -rf /tmp/eliesatpanel-main >/dev/null 2>&1
    fi
print_message "> Eliesatpanel is installed successfully and up to date ..."
echo
sleep 2

print_message "> End of process ..."
echo "-----------------------------------------------"

fi
