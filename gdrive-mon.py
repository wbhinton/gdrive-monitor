from pydrive.auth import GoogleAuth
import io
from pydrive.drive import GoogleDrive
import datetime 
from datetime import timedelta
import email, smtplib, ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import pandas as pd
import pytz

gauth = GoogleAuth()
# get previous auth credentials if available. This prevents the need to re-auth the script with Google. 
# If there is no credentials.txt, then a webserver and browser launches to perform the Auth with Google.
gauth.LoadCredentialsFile("credentials.txt")
if gauth.credentials is None: 
    gauth.LocalWebserverAuth()
elif gauth.access_token_expired:
    gauth.Refresh()
else:
    gauth.Authorize()

gauth.SaveCredentialsFile("credentials.txt")

drive = GoogleDrive(gauth)


# get the file lists and information from the follwoing folders.
folder1 = drive.ListFile({'q': "'--folderid--' in parents and trashed=false"}).GetList()
folder2 = drive.ListFile({'q': "'--folderid--' in parents and trashed=false"}).GetList()
folder3 = drive.ListFile({'q': "'--folderid--' in parents and trashed=false"}).GetList()


# Create dataframes from the dicts created by reading the folder contents
df1 = pd.DataFrame.from_dict(folder1)
df2 = pd.DataFrame.from_dict(folder2)
df3 = pd.DataFrame.from_dict(folder3)


new = pd.concat([df1,df2,df3], axis = 0, sort = False)
new.reset_index()
new['modifiedDate']=pd.to_datetime(new['modifiedDate']) #Converting the modifiedDate field to a Pandas DT 
new1=new.sort_values(by =['modifiedDate'],ascending=False)

df = new1[['title','modifiedDate','alternateLink']]
df.to_csv(r'file-index.csv') #making a copy of the file index in CSV format. 
stop_time = datetime.datetime.now(pytz.utc) # Getting the current time in UTC
start_time = stop_time - timedelta(days = 1) # Setting the start time as 1 day prior.

# Using a mask to filter out everything that was not modified in the last 24hrs
mask = (df['modifiedDate']> start_time) & (df['modifiedDate']<stop_time) 
df1 = df.loc[mask]

#If there are no newly modified files from the previous 24hrs, exit the script.
if df1.empty:

    exit()
# create your email list of everyone that needs a copy of the eamil.
li = ['spamalot@spam.com','ham@spam.com']

#Export the dataframe to HTML 
str_io = io.StringIO()
df1.to_html(buf=str_io,classes = 'table table-striped', columns = ['title','modifiedDate','alternateLink'], max_rows = 10)
html_str = str_io.getvalue()
#print(html_str)

#Sending the email by looping through the list of email addresses.
for i in range(len(li)):

    sender_email = "Monty@HolyGrail.com" # This should be your gmail address.
    receiver_email = li[i]
    password = 'supersecretpassword' # This should be your password for your email client, for gmail use an App Specific password.
    subject = 'Here is a list of all the files that changed in the last 24hrs'

    # Create a multipart message and set headers
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    #message["Bcc"] = receiver_email  # Recommended for mass emails


    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = receiver_email

    # Create the plain-text and HTML version of your message
    # Create the plain-text and HTML version of your message
    text = """\
    This email contains a list of files that were updated yesterday in the Shared Drive.
    """
    html = """\
    <html>
      <body>
        <p>Greetings,<br>
           The table below lists the files that were updated within the last 24hrs on the shared drive.<br>
           <br>
           <br>
           Regards,<br>
           Your Name<br>
           </p>
      </body>
    </html>
    """
    html = html+html_str
    # Turn these into plain/html MIMEText objects
    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")


    # Add HTML/plain-text parts to MIMEMultipart message
    # The email client will try to render the last part first
    message.attach(part1)
    message.attach(part2)


    # Create secure connection with server and send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(
            sender_email, receiver_email, message.as_string()
        )
