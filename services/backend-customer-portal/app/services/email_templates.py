def generate_email_template(user_first_name: str, otp: str) -> str:
    return f"""
    <!DOCTYPE html>
    <html>
    <body>
      <p>Hi {user_first_name},</p>
      <p>Your OTP for login is: <strong>{otp}</strong></p>
      <p>This OTP is valid for 5 minutes.</p>
    </body>
    </html>
    """
