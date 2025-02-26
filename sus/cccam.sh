#!/bin/bash

if [ ! -d /etc/tuxbox/config ]; then
echo "Install an emu 1st,and try again"
exit 1
fi

###########################################
dir="/usr/lib/enigma2/python/Plugins/Extensions/ElieSatPanel/sus/cccam.txt"
if [ ! -s "$dir" ]; then
echo "> url= None"
echo "> port= None"
echo "> username= None"
echo "> username= None"
sleep 2
echo "Write and save a new cccam user , then try again ..." 
sleep 1
exit 1 
fi

# Check for cmd cccam file
###########################################
if [ -f $dir ]; then 
cmdfile=found
sleep 1
else
echo "> cmd file not found"
sleep 1
exit 1 
fi

# determine cccam data
###########################################

label=$(more $dir | tail -n 1 |awk '{print $1}')
echo "> label= $label"
sleep 1
protocol=$(more $dir | tail -n 1 |awk '{print $2}')
echo "> protocol= $protocol"
sleep 1
url=$(more $dir | tail -n 1 |awk '{print $3}')
echo "> url= $url"
sleep 1
port=$(more $dir | tail -n 1 |awk '{print $4}')
echo "> port= $port"
sleep 1
username=$(more $dir | tail -n 1 |awk '{print $5}')
echo "> username= $username"
sleep 1
password=$(more $dir | tail -n 1 |awk '{print $6}')
echo "> password= $password"
sleep 1
echo

# write cccam line data in emus
###########################################
for cam_config_file in oscam ncam
do

if [ -f /etc/tuxbox/config/$cam_config_file.server ]; then
   echo "> $cam_config_file emu config file found"
sleep 1
fi

if ! grep -q $protocol /etc/tuxbox/config/$cam_config_file.server >/dev/null 2>&1; then
:
else
prt=true
sleep 1
fi

if ! grep -q $username /etc/tuxbox/config/$cam_config_file.server >/dev/null 2>&1; then
:
else
ut=true
sleep 1
fi

if ! grep -q $password /etc/tuxbox/config/$cam_config_file.server >/dev/null 2>&1; then
:
else
pt=true
sleep 1
fi

if [[ "$pt" == "true" ]] && [[ "$ut" == "true" ]] && [[ "$prt" == "true" ]]; then
echo "> Your line already exist in $cam_config_file"
sleep 1
else
cat <<EOF >> /etc/tuxbox/config/$cam_config_file.server

[reader]
label                         = $label
protocol                      = $protocol
device                        = $url,$port
user                          = $username
password                      = $password
inactivitytimeout             = 30
group                         = 1
disablecrccws                 = 1
cccversion                    = 2.0.11
cccwantemu                    = 1
ccckeepalive                  = 1
audisabled                    = 1

EOF

   echo "> cccam server installed in $cam_config_file config file successfully"
sleep 3
fi
done

