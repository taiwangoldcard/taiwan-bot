#!/bin/sh
echo "Deploying..."
ssh taiwan-bot /bin/sh << EOF
sudo supervisorctl stop app
cd ~/app
. env/bin/activate
git fetch --all
git reset --hard origin/master
pip install --no-cache-dir -r requirements.txt
sudo supervisorctl start app
EOF
echo "Deployment completed"
