#encoding=utf-8

import smtplib
from email.mime.text import MIMEText
from email.Header import Header
import textwrap

FROM = 'chenyanpeng@dataeye.com'

TO = ["chenyanpeng@dataeye.com"] # must be a list

SUBJECT = "监控"

TEXT = "This message was sent with Python's smtplib."


def send_email(FROM=FROM, TO=TO, SUBJECT=SUBJECT, TEXT=TEXT):

	try:
		msg = MIMEText(TEXT, _charset='UTF-8')
		msg['To'] = ";".join(TO)
		msg['From'] = FROM
		msg['Subject'] = Header(SUBJECT, "UTF-8")
		server = smtplib.SMTP('smtp.exmail.qq.com')
		server.login('chenyanpeng@dataeye.com', 'dc@2013')
		server.sendmail(msg['From'], msg['To'], msg.as_string())
		server.quit()
	except Exception, e:
		pass
