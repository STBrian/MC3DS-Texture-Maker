#!/bin/bash

release_type=$1

if [ "$release_type" == "--debug" ]; then
    if [ -d ./build ]
    then
    rm -r ./build
    fi

    if [ -d ./dist ]
    then
    rm -r ./dist
    fi

    echo "debug" > release_type.txt
    python3.12 -m PyInstaller --noconfirm --clean build.spec
    rm release_type.txt
elif [ "$release_type" == "--release" ]
    if [ -d ./build ]
    then
    rm -r ./build
    fi

    if [ -d ./dist ]
    then
    rm -r ./dist
    fi

    echo "release" > release_type.txt
    python3.12 -m PyInstaller --noconfirm --clean build.spec
    rm release_type.txt
else
    echo "Invalid release type"
fi