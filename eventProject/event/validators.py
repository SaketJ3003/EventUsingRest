import re
from django.contrib.auth.models import User


def validate_username(value):
    if not value or not value.strip():
        raise ValueError("Username is required and cannot be empty.")
    
    if value and User.objects.filter(username=value).exists():
        raise ValueError("Username already Exist")
    
    if value != value.strip():
        raise ValueError("Username cannot have leading or trailing spaces.")
    
    regex = r'^[a-zA-Z0-9]{6,16}$'
    if not re.match(regex, value):
        raise ValueError("Username should have atleast One Uppercase, Lowercase and Digit and It should be between 6 to 16 characters.")
    
    return value


def validate_name(value, allow_spaces=False, field_name="Name"):
    if not value or not value.strip():
        raise ValueError(f"{field_name} is required and cannot be empty.")
    
    if value != value.strip():
        raise ValueError(f"{field_name} cannot have leading or trailing spaces.")

    if allow_spaces:
        regex = r'^[a-zA-Z]+(?: [a-zA-Z]+)*$'
        error_msg = f"{field_name} can only contain alphabetic characters and single spaces"
    else:
        regex = r'^[a-zA-Z]+$'
        error_msg = f"{field_name} can only contain alphabetic characters with no spaces"
    
    if not re.match(regex, value):
        raise ValueError(error_msg)

    return value


def validate_email(value):
    if not value or not value.strip():
        raise ValueError("Email is required and cannot be empty.")
    
    if value and User.objects.filter(email=value).exists():
        raise ValueError("Email already Exist")
    
    if value != value.strip():
        raise ValueError("Email cannot have leading or trailing spaces.")
    regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(regex, value):
        raise ValueError("Invalid Email Format")
    
    return value

def validate_email_login(value):
    if not value or not value.strip():
        raise ValueError("Email is required and cannot be empty.")
    
    if value != value.strip():
        raise ValueError("Email cannot have leading or trailing spaces.")
    regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(regex, value):
        raise ValueError("Invalid Email Format")
    
    return value

def validate_password(value):
    if not value or not value.strip():
        raise ValueError("Password is required and cannot be empty.")
    
    regex = r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[%_@-]).{8,}$'
    if not re.match(regex, value):
        raise ValueError("Password should be of 8 characters, at least 1 capital, 1 small, and numbers with special characters(%,_,-,@)")
    
    return value
