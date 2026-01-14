#!/bin/bash

rel_t=$1

if [[ "$rel_t" = "--debug" || "$rel_t" = "--release" ]]; then
	if [[ -d ./build || -d ./dist ]]; then
		echo "Cleaning..."
	fi
	if [ -d ./build ]; then
		rm -r ./build
	fi
	if [ -d ./dist ]; then
		rm -r ./dist
	fi

	if [[ "$rel_t" = "--debug" ]]; then
		echo "Building debug"
		echo "debug" > release_type.txt
	elif [[ "$rel_t" = "--release" ]]; then
		echo "Building release"
		echo "release" > release_type.txt
	fi

	if command -v python3.14 &> /dev/null; then
		python3.14 -m PyInstaller --noconfirm --clean build.spec
	elif command -v python3.13 &> /dev/null; then
		python3.13 -m PyInstaller --noconfirm --clean build.spec
	elif command -v python3.12 &> /dev/null; then
		python3.12 -m PyInstaller --noconfirm --clean build.spec
	elif command -v python3.11 &> /dev/null; then
		python3.11 -m PyInstaller --noconfirm --clean build.spec
	else
		echo "Please install at least version 3.11 of Python"
	fi
else
	echo "Invalid release type"
fi
