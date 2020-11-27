#!/bin/sh
echo "Deploying..."
ssh taiwan-bot /bin/sh << EOF
sudo supervisorctl stop app
cd ~/app
. .venv/bin/activate
sudo git fetch --all
sudo git reset --hard origin/master
pip install --no-cache-dir -r requirements.txt
sudo supervisorctl start app
EOF
echo "Deployment completed"
