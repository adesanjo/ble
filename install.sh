#!/bin/sh

mkdir -p $HOME/ble
curl https://codeload.github.com/adesanjo/ble/zip/master > $HOME/ble/master.zip

echo "Unzipping..."
unzip -o -qq $HOME/ble/master.zip -d $HOME/ble
rm $HOME/ble/master.zip

echo "Finalising..."
if ! grep -q "export PATH=$PATH:$HOME/ble/ble-master" $HOME/.bashrc
then
    echo "export PATH=$PATH:$HOME/ble/ble-master" >> $HOME/.bashrc
fi
if ! grep -q "export PATH=$PATH:$HOME/ble/ble-master" $HOME/.zshrc
then
    echo "export PATH=$PATH:$HOME/ble/ble-master" >> $HOME/.zshrc
fi

echo
echo "-------------"
echo
echo "BLE Successfully Installed"