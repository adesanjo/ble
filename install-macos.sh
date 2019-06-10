#!/bin/bash

mkdir -p /Applications/ble
curl https://codeload.github.com/adesanjo/ble/zip/master > /Applications/ble/master.zip

echo "Unzipping..."
unzip -o -qq /Applications/ble/master.zip -d /Applications/ble
rm -f /Applications/ble/master.zip

echo "Finalising..."
if [ $SHELL = /bin/bash ]
then
    if [ `grep -c "alias ble=" $HOME/.profile` -eq 0 ]
    then
        echo "alias ble=\"python3 /Applications/ble/ble-master/exe.py\"" >> $HOME/.profile
    fi
    if [ `grep -c "alias blei=" $HOME/.profile` -eq 0 ]
    then
        echo "alias blei=\"python3 /Applications/ble/ble-master/shell.py\"" >> $HOME/.profile
    fi
else
    echo "Your shell was not detected as being bash. Please add /Applications/ble/ble-master to your PATH variable."
fi

echo
echo "-------------"
echo
echo "BLE Successfully Installed"