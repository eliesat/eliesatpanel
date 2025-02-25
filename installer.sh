#!/bin/bash

clear >/dev/null 2>&1

#configuration
###########################################
plugin=main
version='2.60'
changelog='1.25.02.2025'
url=https://github.com/eliesat/eliesatpanel/archive/main.tar.gz
package=/tmp/$plugin.tar.gz
rm -rf /tmp/$plugin.tar.gz >/dev/null 2>&1

# Check script url connectivity and install eliesatpanel
###########################################
if wget -q --method=HEAD https://github.com/eliesat/eliesatpanel/blob/main/installer.sh; then
connection=ok
else
echo "> Server is down, try again later..."
exit 1
fi

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

#check print image and python version
###########################################
if [ -f /etc/image-version ]; then image_version=$(cat /etc/image-version | grep -iF "creator" | cut -d"=" -f2 | xargs) 
elif [ -f /etc/issue ]; then image_version=$(cat /etc/issue | head -n1 | awk '{print $1;}') 
else 
image='> image name not found' 
fi 

python_version=$(python -c "import platform; print(platform.python_version())")

print_message "> Image : $image_version"
sleep 2
print_message "> Python : $python_version"
sleep 2

# check and install libraries
###########################################
# Check python
pyVersion=$(python -c"from sys import version_info; print(version_info[0])")

if [ "$pyVersion" = 3 ]; then
deps+=( "python3-requests" "python3-six" )
else
deps+=( "python-requests" "python-six" )
fi

if [ -f /etc/opkg/opkg.conf ]; then
  STATUS='/var/lib/opkg/status'
  OSTYPE='Opensource'
  OPKG='opkg update'
  OPKGINSTAL='opkg install'
elif [ -f /etc/apt/apt.conf ]; then
  STATUS='/var/lib/dpkg/status'
  OSTYPE='DreamOS'
  OPKG='apt-get update'
  OPKGINSTAL='apt-get install'
fi

install() {
  if ! grep -qs "Package: $1" "$STATUS"; then
    $OPKG >/dev/null 2>&1
    rm -rf /run/opkg.lock >/dev/null 2>&1
    sleep 1
    if [ "$OSTYPE" = "Opensource" ]; then
      $OPKGINSTAL "$1"
      sleep 1
      clear
    elif [ "$OSTYPE" = "DreamOS" ]; then
      $OPKGINSTAL "$1" -y
      sleep 1
      clear
    fi
  fi
}

for i in "${deps[@]}"; do
  install "$i"
done

# Remove unnecessary files and folders
###########################################
[ -d "/CONTROL" ] && rm -r /CONTROL >/dev/null 2>&1
rm -rf /control /postinst /preinst /prerm /postrm /tmp/*.ipk /tmp/*.tar.gz >/dev/null 2>&1

# Download and install eliesatpanel
###########################################
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
fi

# Download and install scripts
###########################################
if [ ! -f /usr/script/Eliesat-Eliesatpanel.sh ] ; then

plugin=main
version='scripts'
url=https://github.com/eliesat/scripts/archive/main.tar.gz
package=/tmp/$plugin.tar.gz
rm -rf /tmp/$plugin.tar.gz >/dev/null 2>&1

wget -qO $package --no-check-certificate $url
tar -xzf $package -C /tmp
extract=$?
rm -rf $package >/dev/null 2>&1

if [ $extract -eq 0 ]; then
    rm -rf /tmp/scripts-main/*.sh >/dev/null 2>&1
    mkdir -p /usr/script >/dev/null 2>&1
    cp -r '/tmp/scripts-main/usr' '/' >/dev/null 2>&1
    rm -rf /tmp/scripts-main >/dev/null 2>&1

print_message "> Eliesatscripts are installed successfully and up to date ..."
sleep 3
fi
fi

print_message "> End of process ..."
sleep 3

print_message "> Please Wait enigma2 restarting. ..."
echo "-----------------------------------------------------------"
sleep 3

# Restart Enigma2 service or kill enigma2 based on the system
############################################
if [ "$OSTYPE" == DreamOS ]; then
    sleep 2
    systemctl restart enigma2
else
    sleep 2
    killall -9 enigma2
fi
