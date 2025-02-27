#!/bin/bash

dir="/usr/lib/enigma2/python/Plugins/Extensions/ElieSatPanel/sus/cccam.txt"
if [ ! -s "$dir" ]; then
echo "> url= None"
echo "> port= None"
echo "> username= None"
echo "> password= None"
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
echo "> label                         = $label"
sleep 1
echo
protocol=$(more $dir | tail -n 1 |awk '{print $2}')
echo "> protocol                      = $protocol"
sleep 1
echo
url=$(more $dir | tail -n 1 |awk '{print $3}')
echo "> url                           = $url"
sleep 1
echo
port=$(more $dir | tail -n 1 |awk '{print $4}')
echo "> port                          = $port"
sleep 1
echo
username=$(more $dir | tail -n 1 |awk '{print $5}')
echo "> username                      = $username"
sleep 1
echo
password=$(more $dir | tail -n 1 |awk '{print $6}')
echo "> password                      = $password"
sleep 1
echo
if [[ "$protocol" == "cccam" ]]; then
echo "> inactivitytimeout             = 30"
sleep 1
echo
echo "> group                         = 1"
sleep 1
echo
echo "> disablecrccws                 = 1"
sleep 1
echo
echo "> cccversion                    = 2.0.11"
sleep 1
echo
echo "> cccwantemu                    = 1"
sleep 1
echo
echo "> ccckeepalive                  = 1"
sleep 1
echo
echo "> audisabled                    = 1"
sleep 1
echo
fi
