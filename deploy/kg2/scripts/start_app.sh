#!/bin/bash
# rename config file
cp /configs/config_secrets.json /mnt/data/orangeboard/kg2/RTX/code/config_secrets.json

# Update database directory permission which is mounted from a PVC
chmod -R 755 /mnt/data/orangeboard/databases/

# the instructions below are from the deployment wiki at https://github.com/RTXteam/RTX/wiki/RTX-KG2-API-Docker-Deployment
su - rt -c 'cd /mnt/data/orangeboard/production/RTX && python3 code/ARAX/ARAXQuery/ARAX_database_manager.py'

sudo service apache2 start
sudo service RTX_OpenAPI_kg2 start
# sudo service RTX_Complete start
# this line is added to stop container completes with exit code 0
tail -f /dev/null
