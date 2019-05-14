#!/bin/sh

rm -rf $HOME/ble
mkdir -p $HOME/ble
curl https://codeload.github.com/adesanjo/ble/zip/master > $HOME/ble/master.zip
cd $HOME/ble
unzip master.zip
rm master.zip
cd $HOME
echo "export PATH=$PATH:$HOME/ble/ble-master" >> .bashrc
echo "export PATH=$PATH:$HOME/ble/ble-master" >> .zshrc
echo
echo "-------------"
echo
echo "BLE Successfully Installed"