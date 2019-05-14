#!/bin/sh

mkdir -p $HOME/ble
curl https://codeload.github.com/adesanjo/ble/zip/master > $HOME/ble/master.zip

echo "Unzipping..."
unzip -o -qq $HOME/ble/master.zip -d $HOME/ble
rm $HOME/ble/master.zip

echo "Finalising..."
if [ $SHELL = /bin/bash ]
then
    if ! echo $PATH | grep -q "$HOME/ble/ble-master"
    then
        echo "export PATH=$PATH:$HOME/ble/ble-master" >> $HOME/.bashrc
    fi
elif [ $SHELL = /bin/zsh ]
then
    if ! echo $PATH | grep -q "$HOME/ble/ble-master"
    then
        echo "export PATH=$PATH:$HOME/ble/ble-master" >> $HOME/.zshrc
    fi
else
    echo "Your shell was not detected as being bash or zsh. Please add $HOME/ble/ble-master to your PATH variable."
fi

echo
echo "-------------"
echo
echo "BLE Successfully Installed"