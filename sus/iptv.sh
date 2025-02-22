#!/bin/bash

dir="/usr/lib/enigma2/python/Plugins/Extensions/ElieSatPanel/sus/iptv.txt"
if [ ! -s "$dir" ]; then
echo "> url= None"
echo "> port= None"
echo "> username= None"
echo "> username= None"
sleep 2
echo "Write and save a new iptv user , then try again ..." 
sleep 1
exit 1 
fi

# determine iptv data
###########################################

url=$(more $dir | head -n 1 |awk '{print $1}')
echo "> url= $url"


port=$(more $dir | head -n 1 |awk '{print $2}')
echo "> port= $port"

username=$(more $dir | head -n 1 |awk '{print $3}')
echo "> username= $username"


password=$(more $dir | head -n 1 |awk '{print $4}')
echo "> password= $password"

declare -A files=(
["bouquetmakerxtream"]="/etc/enigma2/bouquetmakerxtream/playlists.txt"
["jedimakerxtream"]="/etc/enigma2/jediplaylists/playlists.txt"
["xklass"]="/etc/enigma2/xklass/playlists.txt"
["xstreamity"]="/etc/enigma2/xstreamity/playlists.txt"
["e2iplayer"]="/etc/enigma2/e2iplayer/playlists.txt"
["xcplugin"]="/etc/enigma2/xc/xclink.txt"
)

if [ -f "/etc/enigma2/iptosat.conf" ]; then
> /etc/enigma2/iptosat.conf
cat <<EOF >> /etc/enigma2/iptosat.conf
[IPtoSat]
Host=$url
User=$username
Pass=$password
EOF
echo "> your iptv data installed in iptosat config file successfully"
sleep 3
else
echo "> iptosat config file not found"
sleep 3
fi

for playlists in "${!files[@]}"
do
    if [ ! -f "${files[$playlists]}" ]; then
   echo "> $playlists playlists file not found"
   sleep 3
   else
if ! grep -q $username "${files[$playlists]}" >/dev/null 2>&1; then
cat <<EOF >> "${files[$playlists]}"
$url:$port/get.php?username=$username&password=$password&type=m3u
EOF
echo "> your iptv data installed in $playlists playlists file successfully"
sleep 3
else
echo "> your iptv data already installed in $playlists playlists file"
sleep 3
fi
   fi
done

