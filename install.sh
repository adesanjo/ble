#!/bin/sh

mkdir -p $HOME/ble
curl https://github.com/adesanjo/ble/archive/master.zip > $HOME/ble/master.zip
cd $HOME/ble
unzip master.zip