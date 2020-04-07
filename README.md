# pm-server-python
HTTP Server for Church Membership Database (Peri Meleon)

## Install
git clone git@github.com:MidnightJava/pm-server-python

cd pm-server-python

python3 -m pip install -r requirements.txt

## Run
python3 ./src/server.py

## Access
### Get COMMUNING and NONCOMMUNING members
curl localhost:8000/api/getMembers?scope=active

### Get all members
curl localhost:8000/api/getMembers?scope=all 
