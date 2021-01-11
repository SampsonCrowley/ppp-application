# -*- coding: utf-8 -*-
"""Application views."""
from .forms import ApplicationForm
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    flash,
    jsonify,
    url_for,
    render_template_string,
    escape,
    current_app
    )
from flask_login import login_required
from flask_wtf.csrf import CSRFProtect,CSRFError
from werkzeug.utils import secure_filename
import csv
import os
import time
import uuid
import phonenumbers
import magic
import traceback

blueprint = Blueprint("application", __name__, url_prefix="/applications", static_folder="../static")

###################
# UPLOAD VALIDATION
####################
def allowed_ext(filename):
    if not "." in filename:
        return False

    ext = filename.rsplit(".", 1)[1]

    if ext.upper() in current_app.config["ALLOWED_FILE_EXTENSIONS"]:
        return True
    else:
        return False

def allowed_mime(mime):
    return True if current_app.config["ALLOWED_MIME_TYPES"].match(mime) else False

def get_mimetype(file):
    f = magic.Magic(mime=True)
    res = f.from_buffer(file.stream.read(2048))
    file.stream.seek(0)
    return res

def allowed_filesize(filesize):
    print(int(filesize))
    print(filesize)
    return 0 < int(filesize) <= current_app.config["MAX_FILE_SIZE"]

def get_filesize(file):
    file.seek(0, os.SEEK_END)
    fileLength = file.tell()
    file.seek(0, 0)
    return fileLength

@blueprint.route('/', methods=["GET"])
def index():
    return render_template("applications/index.html", form=ApplicationForm())

@blueprint.route('/', methods=["POST"])
def upload():
    try:
        form = ApplicationForm()
        print(form.data)
        file = request.files.get('files[]')

        # Check if valid post request
        if form.validate_on_submit():
        
            # Retreive form inputs
            fName = form.firstName.data
            lName = form.lastName.data
            email = form.email.data
            phone = form.phone.data
            business = form.business.data
            startDate = form.startDate.data
            tin = form.tin.data
            naics = form.naicsCode.data
            loanNumber = form.loanNumber.data
            loanOfficer = form.loanOfficer.data

            # Set upload and directory data
            parent_path = os.path.join(current_app.root_path, "client", "uploads")
            business_secure = secure_filename(business)
            tin_secure = secure_filename(tin)
            path = os.path.join(parent_path, tin_secure + '-' + business_secure)

            uploads = request.files.getlist('files[]')

            if business is None or "None" in path:
                if tin is None:
                    raise Exception("Failed to get a directory path for upload")

            # Create upload directory if path doesn't exist
            if not os.path.exists(path) and business is not None and not "None" in path:
                if tin is not None:
                    print(f"creating directory: {path}")
                    os.makedirs(path)
                    csvfilename = 'customerinfo.csv'
                    csvpath = os.path.join(path, csvfilename)

                    # Generate cusotmer info CSV
                    with open(csvpath, 'w', newline='') as csvfile:
                        fieldnames = [
                            'First Name',
                            'Last Name',
                            'Email',
                            'Phone',
                            'Start Date',
                            'Business',
                            'TIN',
                            'NAICS',
                            'Loan #',
                            'Loan Officer'
                            ]
                        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                        writer.writeheader()
                        writer.writerow({
                            'First Name': fName,
                            'Last Name': lName,
                            'Email': email,
                            'Phone': phone,
                            'Business': business,
                            'TIN': tin,
                            'NAICS': naics,
                            'Loan #': loanNumber,
                            'Loan Officer': loanOfficer
                            })

            # Loop through each file and upload
            valid = "Files must be a PDF or Image no larger than 5MB"
            if uploads:
                for f in uploads:

                    if allowed_ext(f.filename) and allowed_filesize(get_filesize(f)) and allowed_mime(get_mimetype(f)):
                        # Get filename
                        filename = secure_filename(f.filename)
                        uniqueid = uuid.uuid4().hex
                        refile = uniqueid + '_' + filename
                        filepath = os.path.join(path, refile)
                        print(f"saving file to directory: {filepath}")
                        f.save(filepath)
                        if not os.path.exists(filepath):
                            raise Exception(f"Failed to save file: {filename}; {valid}")
                    else:
                        raise Exception(f"Invalid file: {f.filename}; {valid}" if f else f"Invalid file; {valid}")
                    
            else:
                raise Exception("No files given")

        else:
            raise Exception('Not a valid post request')

    except Exception as e:
        print(type(e))
        message = str(e)
        print(message)
        if message == "Not a valid post request":
            return jsonify({"succes": False, "type": "validation", "errors": form.errors}), 422
        else:
            return jsonify({"success": False, "type": "error", "message": message}), 422
    else:
        print("Everything didn't fail whoo hoo")
        return jsonify({"success": True, "redirect": "/applications/success"})

@blueprint.errorhandler(CSRFError)
def csrf_error(e):
    return e.description, 400

@blueprint.route("/new-csrf")
def generate_csrf():
    return jsonify({"token": escape(ApplicationForm().csrf_token)})

@blueprint.route("/success")
def success():
    return render_template("applications/success.html")
