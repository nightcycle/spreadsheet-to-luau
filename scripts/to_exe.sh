#!/bin/bash
# python src/setup.py install
pyinstaller --onefile src/__init__.py -n spreadsheet-to-luau
# pyinstaller __init__.spec
