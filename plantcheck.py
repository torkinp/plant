# This script is designed to check the water monitor sensor once, rarther 
# than to loop. So use CRON to call the script at the required
# frequency/time.
# Wake up the sesnor, pause, test it's value then send an email
# if the plant needs watering.
#
# It now also writes to a log file showing activity and errors/debug into.
#

# need to get current working directory, so import 'os'
import os

# import logging module
import logging

# smtplib provides email sending
import smtplib

# libs to support more sophisticated
# email formatting and attachments
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# GPIO lib
import RPi.GPIO as GPIO 

# we need time functions
import time

# a function to send the email (with an attachment)
def sendEmail():
    try:
        fromaddr = "rpibvr@gmail.com"
        toaddr = "pete@torkington.me"
        msg = MIMEMultipart()
        msg['From'] = fromaddr
        msg['To'] = toaddr
        msg['Subject'] = "you can water me now"
        body = "Hi,\n\nIt's time to water me please.\n\nKind regards,\nplant"
        msg.attach(MIMEText(body, 'plain'))
        # set the filename and path
        filename = "plant.jpg"
        path = os.getcwd() + "/"
        attachment = open(path + filename, "rb")

        part = MIMEBase('application', 'octet-stream')
        part.set_payload((attachment).read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', "attachment; filename= %s" % filename)
        
        msg.attach(part)

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(fromaddr, "raspberryRPI")
        text = msg.as_string()
        server.sendmail(fromaddr, toaddr, text)
        server.quit()
    
    except SMTPException:
        print("Error: unable to send email")


# code starts here :)

# Set up logging
LOG_FILENAME = 'plantinfo.log'
path = os.getcwd() + "/"
logging.basicConfig(filename=path + LOG_FILENAME,level=logging.DEBUG)

# let's use BCM referencing for GPIO
GPIO.setmode(GPIO.BCM)

# GPIO 17 is our digital sensor input
GPIO.setup(17, GPIO.IN)
# GPIO 27 is used to power the digital sensor board when polling.
GPIO.setup(27, GPIO.OUT)



#
# ok, let's sense the moisture and take action if needed.

# send power to the sensor
GPIO.output(27, GPIO.HIGH)
localtime = time.asctime( time.localtime(time.time()) )
logging.info(localtime + " Enabling moisture sensor")

# let's just pause for a while (10 mins), let the sensor settle
time.sleep(6)

# As the moisture sensor is digital, it returns high if dry,
# returning low if moisture is detected.
# So, if pin 17 is high, the plant is dry, send an email
localtime = time.asctime( time.localtime(time.time()) )
if GPIO.input(17):
    logging.info(localtime + " *** Water Me! ***")
    sendEmail()
else:
    logging.info(localtime + " Don't water me.")

# cease power to the sensor
GPIO.output(27, GPIO.LOW)
GPIO.cleanup()
