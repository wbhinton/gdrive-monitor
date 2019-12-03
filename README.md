# Google Drive Shared Folder Monitor

This script will check a list of Google Drive folders for any additions in the previous 24hrs and logs the files into a CSV. If there are changes it will send an email with a table of all of the new files and links to their location on GDrive. I created this because I was having trouble finding a solution that allowed me to monitor a single *shared with me* folder and send email updates to a group.

## Setup
I will assume you have python setup and know how to install modules via pip or conda

1. Install the required modules. 
``` sh
pip install pydrive pandas pytz
```
2. Download the gdrive-mon.py file and place it in your home folder
3. Make the file executable: 
```
chmod +x ~/gdrive-mon.py
```
4. Edit gdrive-mon.py to include the links to the folders you want to monitor. To do this, navigate to the folder in Google Drive, then copy the link in the address bar and paste it into the script. You will also want to update the email list in the script to include everyone that needs to be updated on the folder contents. 

5. Execute the file manually for the first time to initiate GAuth and save your credentials. This will open up a browser window and request permission for this script to access your Google Drive. You should only have to do this once, the auth key is saved in the working directory as 'credentials.txt:
```
python gdrive-mon.py
```

6. Your script is setup, now you need to schedule it to run. 

## Automation 

If you are using Linux, you can setup systemd timers to execute the script on a schedule for you. [Systemd Timers](https://wiki.archlinux.org/index.php/Systemd/Timers) or you can setup a traditional cron job using [Cron](https://wiki.archlinux.org/index.php/Cron)

For example I am using systemd timers and run the script every morning to check for any new files in a shared folder. 
