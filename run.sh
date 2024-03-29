#!/bin/bash

# To make double clicking cbscript files work,
# modify the defaults of your desktop environment.
#
# To generate blocks.json, via command prompt at the minecraft server:
# java -DbundlerMainClass=net.minecraft.data.Main -jar {jar_path} --server --reports

echo "CBScript 1.20"

if [ $# -eq 0 ]; then
    echo "No script provided."
    exit
fi

if ! [ -f $1 ]; then
    echo "Please provide a valid file."
    exit
fi

echo -ne "\033]0;$(basename $1)\007"
pushd $(dirname $0)
python3 compile.py $1
popd

read -p "Press enter to continue..."
