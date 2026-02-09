import asyncio
import logging
from app.services.otp_service import OTPService

# Configure logging
logging.basicConfig(level=logging.INFO)

async def main():
    phone = "+919876543210"  # Replace with your test phone number
    email = "shindepayal296@gmail.com"  # Replace with your test email

    print("=== TESTING OTP SERVICE ===")

    # Send OTP
    print("Sending OTP...")
    response = await OTPService.send_otp(phone=phone, email=email)
    print("Send OTP Response:", response)

    otp_code = response.get("otp_code")
    if not otp_code:
        print("No OTP code returned (maybe production mode).")
        return

    # Verify OTP
    print(f"Verifying OTP {otp_code} for phone {phone}...")
    try:
        result = await OTPService.verify_otp(phone=phone, otp_code=otp_code)
        print("OTP verification result:", result)
    except Exception as e:
        print("OTP verification failed:", e)

    # Send password reset OTP
    print("\nSending password reset OTP...")
    reset_response = await OTPService.send_otp_for_password_reset(email=email)
    print("Password Reset OTP Response:", reset_response)

    otp_reset_code = reset_response.get("otp_code", otp_code)
    print(f"Verifying password reset OTP {otp_reset_code} for email {email}...")
    try:
        result_reset = await OTPService.verify_otp_for_password_reset(email=email, otp_code=otp_reset_code)
        print("Password reset OTP verification result:", result_reset)
    except Exception as e:
        print("Password reset OTP verification failed:", e)

# Run the async main function
asyncio.run(main())
