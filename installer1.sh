#!/bin/bash

clear >/dev/null 2>&1

#configuration
###########################################
plugin=main
version='3.06'
changelog='1.25.08.2025'
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


echo "hi this is a test"
sleep 60
