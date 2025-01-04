REGISTER_OTP_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Register OTP</title>
</head>
<body>
    <h2>Welcome! {name}</h2>
    <p>Your OTP for registration is: {otp}</p>
</body>
</html>
"""

LOGIN_OTP_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Login OTP</title>
</head>
<body>
    <h2>Hello! {name}</h2>
    <p>Your OTP for login is: {otp}</p>
</body>
</html>
"""

RESET_OTP_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Password Reset OTP</title>
</head>
<body>
    <h2>Hello! {name}</h2>
    <h2>Password Reset Request</h2>
    <p>Your OTP for password reset is: {otp}</p>
</body>
</html>
"""
