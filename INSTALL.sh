#!/bin/bash

cd ~/.local/
echo "Downloading shellrhythm to ~/.local/..."
git clone https://github.com/HastagGuigui/shellrhythm.git
cd ./shellrhythm
echo "Installing required python dependencies... (there's like 3)"
pip install -r requirements.txt
echo "Linking ~/.local/shellrhythm/shellrhythm to ~/.local/bin/shellrhythm..."
ln -s ~/.local/shellrhythm/shellrhythm ~/.local/bin/shellrhythm
echo "Successfully installed! You can now run the shellrhythm command to begin."
echo "(If the command is not recognised, restart your terminal.)"