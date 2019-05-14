#!/bin/sh

mkdir -p $HOME/ble
curl https://codeload.github.com/adesanjo/ble/zip/master > $HOME/ble/master.zip
cd $HOME/ble
unzip -o -qq master.zip
rm master.zip
cd $HOME
echo "export PATH=$PATH:$HOME/ble/ble-master" >> $HOME/.bashrc
echo "export PATH=$PATH:$HOME/ble/ble-master" >> $HOME/.zshrc

echo
echo "-------------"
echo
echo "BLE Successfully Installed"