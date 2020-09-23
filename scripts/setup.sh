#!/bin/sh
# environment assumes an ubuntu 20.04, please setup your ~/.ssh/config first
ssh taiwan-bot /bin/sh << EOF
pip3 install virtualenv
git clone https://github.com/taiwangoldcard/taiwan-bot.git app
cd app
~/.local/bin/virtualenv -p /usr/bin/python3 env
. env/bin/activate
pip install --no-cache-dir -r requirements.txt
deactivate
EOF
