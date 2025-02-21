#!/bin/bash

dir="/usr/lib/enigma2/python/Plugins/Extensions/ElieSatPanel/sus/iptv.txt"

# Check for cmd cccam file
###########################################
if [ -f $dir ]; then 
cmd=found
sleep 1
else
echo "> cmd file not found"
sleep 1
exit 1 
fi

# determine iptv data
###########################################

url=$(more $dir | head -n 1 |awk '{print $1}')
echo $url


port=$(more $dir | head -n 1 |awk '{print $2}')
echo $port


username=$(more $dir | head -n 1 |awk '{print $3}')
echo $username


password=$(more $dir | head -n 1 |awk '{print $4}')
echo $password


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
$url/get.php?username=$username&password=$password&type=m3u_plus
EOF
echo "> your iptv data installed in $playlists playlists file successfully"
sleep 3
else
echo "> your iptv data already installed in $playlists playlists file"
sleep 3
fi
   fi
done
