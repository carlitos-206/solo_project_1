from functools import total_ordering
from sre_constants import error
from django.db import models
import re
from django.db.models.deletion import CASCADE
from django.db.models.fields import TimeField
import bcrypt
from datetime import datetime, time, date, timedelta

#---------------------The models below: Users and UserManager--------------------------------

class UserManager(models.Manager):
    def user_validation(request, postData):
        errors={}
        EMAIL_REGEX=re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
        PASSWORD_REGEX= re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{6,20}$')
        email_exist=Users.objects.filter(email=postData['email'])
        username_exist=Users.objects.filter(username=postData['username'])
        special_char=['!', '@', '#', '$', '%', '&', '?' ]
        if len(postData['first_name'])<2:
            errors["first_name"]="First Name needs to be more than 2 character"
        if len(postData['last_name'])<2:
            errors["last_name"]="Last Name needs to be more than 2 characters"
        if not EMAIL_REGEX.match(postData['email']):
            errors["email"]="Invalid Email"
        if email_exist:
            errors["email_exist"]="Email already exist"
        
        if not PASSWORD_REGEX.match(postData['password']):
            errors["password"]="Password invalid "
        if username_exist:
            errors["username_exist"]="Username is taken"
        if len(postData['password'])<8:
            errors["pw_too_short"]="Password too short needs to be least 8 characters"
        if len(postData['password'])>20:
            errors["pw_too_long"]="Keep password under 20 characters"
        if not any(char in special_char for char in postData['password']):
            errors['no_special_char_pw']=f"Password needs one special character: {special_char}"
        if not any(char.isdigit() for char in postData['password']):
            errors['no_int_pw']="Password needs least one number"
        if not any(char.isupper() for char in postData['password']):
            errors['no_upper_pw']="Password needs one uppercase letter"
        if not any(char.islower() for char in postData['password']):
            errors['no_lower_pw']="Password needs one lowercase letter"
        if postData['password'] != postData['pw_confirmation']:
            errors["pw_no_match"]='Password fields need to match'
        return errors
    def login_validation(request, password, username):
        existing_user=Users.objects.filter(username=username)
        if existing_user:
            existing_user[0]
            if bcrypt.checkpw(password.encode(), existing_user[0].password.encode()):
                return True
            else:
                return False
class Users(models.Model):
    first_name=models.CharField(max_length=255)
    last_name=models.CharField(max_length=255)
    email=models.CharField(max_length=255)
    gender=models.CharField(max_length=255)
    username=models.CharField(max_length=255)
    password=models.CharField(max_length=255)
    profile_pic=models.FileField()
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    objects=UserManager()

#---------------------------END-----------------------------------------

#------------------Models below: Party and PartyManager---------------------

class PartyManager(models.Manager):
    def basic_validator(self, postData):
        errors={}
        partyDate=datetime.strptime(postData['date'], '%Y-%m-%d')
        yesterday=datetime.today()- timedelta(days=1)
        if len(postData['title']) < 1:
            errors['title_error']='Missing Party name'
        if  len(postData['location']) < 2:
            errors['location_error']="Missing Location"
        if 0 < len(postData['rules']) < 1:
            errors['rules_error']= 'Rules needs to be more explicit'
        if len(postData['date']) < 1:
            errors['missing_date']="Missing Date"
        if  partyDate<=yesterday:
                errors['date_past']="Can't time travel make sure date is at least tomorrow"
        if 0 < len(postData['items_needed']) < 2:
            errors['items_error']='Be more descriptive of what you need to party'
        return errors

class Party(models.Model):
    title=models.CharField(max_length=255)
    location=models.CharField(max_length=255)
    rules=models.CharField(max_length=255)
    date=models.DateField()
    time=models.TimeField()
    items=models.TextField()
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    host=models.ForeignKey(Users, on_delete=CASCADE)
    joined=models.ManyToManyField(Users, related_name='rsvp')
    objects=PartyManager()
