#!/bin/sh
echo "" >> ~/.zshrc
echo "# flowの設定" >> ~/.zshrc
cat ./flow.sh >> ~/.zshrc
echo "" >> ~/.zshrc
echo 'fpath=(~/.zsh $fpath)' >> ~/.zshrc
cp ./_flow.sh ~/.zsh/_flow
cp ./flow.py ~/.flow.py