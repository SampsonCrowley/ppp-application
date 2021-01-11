# -*- coding: utf-8 -*-
"""Public forms."""
from flask import Flask, render_template, request, redirect, flash, jsonify, url_for, render_template_string, escape
from flask_wtf import FlaskForm, RecaptchaField
from werkzeug.utils import secure_filename
from wtforms import TextField, BooleanField, StringField, PasswordField, IntegerField, FileField, MultipleFileField, DateField, SelectField
from wtforms import FileField, MultipleFileField, SelectField, ValidationError
from wtforms.fields.html5 import IntegerField, DateField, EmailField
from wtforms.validators import InputRequired, Length, NumberRange, Email, DataRequired, Regexp, AnyOf, Optional
from flask_wtf.csrf import CSRFProtect, CSRFError
import csv
import os
import time
import uuid
import phonenumbers
import magic
import traceback

from ppp_application.user.models import User

class ApplicationForm(FlaskForm):

    ################ 
    # SELECT FIELDS
    ################
    officerChoices = [
        ('--Select--'),
        ('Annette Smith'),
        ('Brad Peterson'),
        ('Brent Wallis'),
        ('Brian Webster'),
        ('Bruce G. Jensen'),
        ('Bruce Rigby'),
        ('Clay Denos'),
        ('Clint Buys'),
        ('Craig Maughan'),
        ('Curt Beutler'),
        ('Dan Balls'),
        ('Danny Johnson'),
        ('Darrell Simmons'),
        ('Darren Cole'),
        ('Darren Dyreng'),
        ('David Ames'),
        ('Don Coombs'),
        ('Jacob Israelsen'),
        ('Jake Miller'),
        ('Jason Morrell'),
        ('John T. Jones'),
        ('Jory Spotts'),
        ('Kathryn A. Beus'),
        ('Kelly West'),
        ('Kevin Madsen'),
        ('Kyle Neva'),
        ('Lance Zollinger'),
        ('Mark Howells'),
        ('Michael Miller'),
        ('Morgan Gubler'),
        ('Roy Savage'),
        ('Russ Imlay'),
        ('Ryan Anderson'),
        ('Ryan Marrelli'),
        ('Seth Taft'),
        ('Sheldon Banks'),
        ('Shelly Harris'),
        ('Sid G. Beckstead'),
        ('Timothy Frame'),
        ('Travis Phillips'),
        ('Trudi Stilson'),
        ('Tyler Obray')
    ]

    naicsChoices = [
        ('--Select--'),
        ('11: Agriculture, Forestry, Fishing and Hunting'),
        ('21: Mining'),
        ('22: Utilities'),
        ('23: Construction'),
        ('31-33: Manufacturing'),
        ('42: Wholesale Trade'),
        ('44-45: Retail Trade'),
        ('48-49: Transportation and Warehousing'),
        ('51: Information'),
        ('52: Finance and Insurance'),
        ('53: Real Estate rental and Leasing'),
        ('54: Professional, Scientific, and Technical Services'),
        ('55: Management of Companies and Enterprises'),
        ('56: Administrative and Support Waste Management and Remediation Services'),
        ('61: Educational Services'),
        ('62: Health Care and Social Assistance'),
        ('71: Arts, Entertainment, and Recreation'),
        ('72: Accommodation and Food Services'),
        ('81: Other Services (except Public Administration)'),
        ('92: Public Administration')
    ]

    firstName = StringField(
        '*First Name',
        validators=[
            InputRequired("Enter your name."),
            Regexp((r'^[\w ]+$'), message="This field does not allow special characters."),
            Length(min=1, message="This field may not be left blank.")
        ])
    lastName = StringField(
        '*Last Name',
        validators=[
            InputRequired("Enter your name."),
            Regexp((r'^[\w ]+$'), message="This field does not allow special characters."),
            Length(min=1, message="This field may not be left blank.")
        ])
    email = EmailField(
        '*Email',
        render_kw={"placeholder": "example@example.com"},
        validators=[
            InputRequired("Enter your email."),
            Email("Invalid email address. Please try again."),
            validate_length(min=6, max=50)
        ])
    phone = StringField(
        '*Phone',
        validators=[
            InputRequired("Enter your phone number."),
            Length(min=10, message="Phone number must be at least 10 digits."),
            validate_phone
        ])
    business = StringField(
        '*Business Name',
        validators=[
            InputRequired("Enter your business name."),
            Regexp((r'^[\w ]+$'), message="This field does not allow special characters."),
            Length(min=2, message="This field may not be left blank.")
        ])
    tin = StringField(
        '*TIN or SSN',
        render_kw={"placeholder": "9-Digit TIN or SSN if Sole Proprietor (No Dashes)"},
        validators=[
            InputRequired("Enter your 9 digit TIN or SSN without a dash."),
            Length(min=9, max=9, message="The TIN or SSN may only be 9 digits in length and not contain any special characters. Please try again."),
            Regexp((r'^[0-9]*$'), message="The TIN or SSN may only be 9 digits in length and not contain any special characters. Please try again.")
        ])
    startDate = DateField(
        '*Start Date',
        validators=[InputRequired("Enter the start date of your business.")],
        format="%Y-%m-%d"
        )
    loanOfficer = SelectField(
        'Loan Officer (Skip if None)',
        choices=officerChoices,
        validate_choice=False
        )
    loanNumber = StringField(
        "Round 1 Loan #",
        render_kw={"placeholder": "10-Digit Loan # Leave blank if you didn't receive a PPP loan (No Dashes)"},
        validators=[
            validate_loan,
            Regexp((r'^[0-9]*$'), message="This field does not allow special characters.")
        ])
    naicsCode = SelectField('NAICS Code (Skip if None)', choices=naicsChoices, validate_choice=False)
    # image = FileField('image')
    recaptcha = RecaptchaField()


class LoginForm(FlaskForm):
    """Login form."""

    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        """Create instance."""
        super(LoginForm, self).__init__(*args, **kwargs)
        self.user = None

    def validate(self):
        """Validate the form."""
        initial_validation = super(LoginForm, self).validate()
        if not initial_validation:
            return False

        self.user = User.query.filter_by(username=self.username.data).first()
        if not self.user:
            self.username.errors.append("Unknown username")
            return False

        if not self.user.check_password(self.password.data):
            self.password.errors.append("Invalid password")
            return False

        if not self.user.active:
            self.username.errors.append("User not activated")
            return False
        return True
