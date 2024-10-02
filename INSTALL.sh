#!/usr/bin/env sh

if [ "$(tput colors)" -gt 2 ]; then
  RED="\033[1;31m"
  RESET="\033[0m"
else
  RED=""
  RESET=""
fi

error() {
  echo "${RED}Error: $1${RESET}"
  echo "Please report this at \
https://github.com/shellrhythm/shellrhythm-cli/issues if necessary."
  exit 1
}

cd ~/.local/

echo "Downloading shellrhythm to ~/.local/..."
git clone https://github.com/HastagGuigui/shellrhythm.git --depth=1
[ $? -ne 0 ] && error "Failed to download shellrhythm from GitHub"

cd ./shellrhythm

echo "Installing required python dependencies... (there's like 3)"
python3 -m pip install -r requirements.txt
[ $? -ne 0 ] && error "Failed to download python dependencies"

echo "Linking ~/.local/shellrhythm/shellrhythm to ~/.local/bin/shellrhythm..."
ln -s ~/.local/shellrhythm/shellrhythm ~/.local/bin/shellrhythm
[ $? -ne 0 ] && error "Failed to create symbolic link"

echo "Successfully installed! You can now run the shellrhythm command to begin."
echo "(If the command is not recognised, restart your terminal.)"
