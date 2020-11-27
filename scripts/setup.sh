#!/bin/sh
# environment assumes an ubuntu 20.04, please setup your ~/.ssh/config first
ssh taiwan-bot /bin/sh << EOF
sudo pip3 install virtualenv
sudo git clone https://github.com/taiwangoldcard/taiwan-bot.git app
cd app
virtualenv .venv
. .venv/bin/activate
pip install --no-cache-dir -r requirements.txt
deactivate
EOF
