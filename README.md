# Raspberripichatserver
a web server chat space running on a raspberry pi
when you run this code you will be running a chat server from your raspberry pi on your network

put the file on your desktop (file is provoded in repositorie)

in your raspberry pi terminal run-

cd Desktop
--------------------------------------
unzip chat_web_private.zip
--------------------------------------
cd chat_web_private
--------------------------------------
python3 -m venv venv
--------------------------------------
source venv/bin/activate
--------------------------------------
pip install flask flask-socketio eventlet
--------------------------------------
python app.py






then in your browser visit             http://<thepiip>:5000/room/roomname     IMPORTANT NOTE "replace <thepiip>" with your Raspberry Pi ip

chat_web_private.zip ; beta v1
NOTE the README instructions are only up to date with the most recent release of the private rooms chat server
