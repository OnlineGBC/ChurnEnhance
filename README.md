# OpinionJournalism
Using Research done independently create articles, titles, sub-headings, hashtags and social media post

# Before starting run these installs:
#  pip install openai-whisper
#  sudo apt-get update and sudo apt-get install ffmpeg
#  tested on python3.12

sudo apt install python-is-python3
sudo apt update
pip install openpyxl
pip install streamlit-autorefresh
pip install extract-msg
sudo apt-get install tesseract-ocr
sudo apt install python3-pip
sudo apt install python3.12-venv
python3 -m venv DataCleansing2
source DataCleansing2/bin/activate
pip install streamlit
# sudo setcap 'cap_net_bind_service=+ep' /usr/bin/python3.12
#       Not used setcap here because we used port 8443 ~/DataCleaning2/streamlit/config.toml  
# (as noted above, since it was tested on python3.12.  If needed, use another version but test as needed)

Run in foreground:  streamlit run app.py

To Run in background:
sudo apt-get update
sudo apt-get install supervisor

sudo nano /etc/supervisor/conf.d/DataCleansing2.conf
Contents:
    [program:DataCleansing2]
    # command=STREAMLIT_CONFIG_FILE=/home/developer/DataCleansing2/.streamlit/config.toml /home/developer/DataCleansing2/DataCleansing2/bin/streamlit run /home/developer/DataCleansing2/app.py
    command=/bin/sh -c 'STREAMLIT_CONFIG_FILE=/home/developer/DataCleansing2/.streamlit/config.toml /home/developer/DataCleansing2/DataCleansing2/bin/streamlit run /home/developer/DataCleansing2/app.py'
    directory=/home/developer/DataCleansing2
    user=developer
    autostart=true
    autorestart=true
    redirect_stderr=true
    stdout_logfile=/var/log/supervisor/DataCleansing2.log
    stderr_logfile=/var/log/supervisor/DataCleansing2_err.log

Next give these commands:
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl status

Checking logs:
tail -f /var/log/supervisor/streamlit.log
tail -f /var/log/supervisor/streamlit_err.log

Stop/Start process:
sudo supervisorctl stop DataCleansing2
sudo supervisorctl start DataCleansing2
sudo supervisorctl restart DataCleansing2
sudo supervisorctl status DataCleansing2








