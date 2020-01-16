import smtplib


def send_mail(to, otp):
    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login("sahilt.spaceo@gmail.com", "sahil@1511")

        SUBJECT = "Reset Password"
        TEXT = "Your one time password is: " + otp + ". It will expire in 10 minutes."
        message = 'Subject: {}\n\n{}'.format(SUBJECT, TEXT)

        from_ = 'sahilt.spaceo@gmail.com'

        server.sendmail(
            from_,
            to,
            message)
        server.quit()
        print("Mail sent")
        return True
    except:
        return False
