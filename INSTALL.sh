#!/bin/bash

cd ~/.local/
echo "Downloading shellrhythm to ~/.local/..."
git clone https://github.com/HastagGuigui/shellrhythm.git
cd ./shellrhythm
echo "Installing required python dependencies... (there's like 3)"
pip install -r requirements.txt
echo "Linking ~/.local/shellrhythm/shellrhythm to ~/.local/bin/shellrhythm..."
ln -s ~/.local/shellrhythm/shellrhythm ~/.local/bin/shellrhythm
echo "Successfully installed, however, it may not fully work!"
echo "(More informations are given in ./docs/PYBASS3_LINUX.md.)"
#TODO: actually automatise this part! I am way too lazy to.
echo "Either way, once that extra step is done, type \"shellrhythm\" from anywhere to begin!"
echo "(If the command is not recognised, restart your terminal.)"