#!/bin/sh
echo "Deploying..."
ssh taiwan-bot /bin/sh << EOF
sudo supervisorctl stop app
cd ~/app
. env/bin/activate
git pull
pip install --no-cache-dir -r requirements.txt
sudo supervisorctl start app
EOF
echo "Deployment completed"
