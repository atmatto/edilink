#!/bin/bash

rm -r ~/.local/share/Anki2/addons21/edilink/
mkdir ~/.local/share/Anki2/addons21/edilink/
cp -r __init__.py config.md manifest.json ~/.local/share/Anki2/addons21/edilink/
anki