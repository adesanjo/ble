#!/bin/bash

mkdir -p /Applications/ble
curl https://codeload.github.com/adesanjo/ble/zip/master > /Applications/ble/master.zip

echo "Unzipping..."
unzip -o -qq /Applications/ble/master.zip -d /Applications/ble
rm -f /Applications/ble/master.zip

echo "Finalising..."
if [ $SHELL = /bin/bash ]
then
    if ! alias | grep "ble="
    then
        echo "alias ble=\"python3 /Applications/ble/ble-master/exe.py\"" >> /Applications/.profile
    fi
    if ! alias | grep "blei="
    then
        echo "alias blei=\"python3 /Applications/ble/ble-master/shell.py\"" >> /Applications/.profile
    fi
else
    echo "Your shell was not detected as being bash. Please add /Applications/ble/ble-master to your PATH variable."
fi

echo
echo "-------------"
echo
echo "BLE Successfully Installed"