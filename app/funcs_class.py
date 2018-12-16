# General
from os import path, mkdir, remove, urandom
from flask import flash, url_for
from flask_login import current_user
from time import time
# Models
from app.models import Token
# Tokens
from binascii import hexlify
# Email
from smtplib import SMTP
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
# Database
from app import db


class FilesPath:
    def __init__(self, user=current_user):
        self.id = str(user.id)
        self.files_path_dir = path.join(path.dirname(path.abspath(path.realpath(__file__))), 'static', 'files', self.id)
        self.files_path_private = path.join(self.files_path_dir, 'private')
        self.files_path_public = path.join(self.files_path_dir, 'public')
        self.files_path_avatar = path.join(path.dirname(path.abspath(path.realpath(__file__))), 'static', 'avatars')

    def public(self, filename=None, type=None):
        if type is not None and filename is not None:
            if not path.isdir(path.join(self.files_path_public, type)):
                mkdir(path.join(self.files_path_public, type))
            return path.join(self.files_path_public, type, filename)
        elif filename is not None:
            return path.join(self.files_path_public, filename)
        else:
            return self.files_path_public

    def private(self, filename=None, type=None):
        if type is not None and filename is not None:
            if not path.isdir(path.join(self.files_path_private, type)):
                mkdir(path.join(self.files_path_private, type))
            return path.join(self.files_path_private, type, filename)
        elif filename is not None:
            return path.join(self.files_path_private, filename)
        else:
            return self.files_path_private

    def isfile(self, repo='public', filename=None, type="misc"):
        if repo == "public":
            return path.isfile(path.join(self.files_path_public, type, filename))
        elif repo == "private":
            return path.isfile(path.join(self.files_path_private, type, filename))
        elif repo is None:
            return path.isfile(filename)

    def isdir(self):
        return path.exists(self.files_path_dir)

    def newdir(self):
            mkdir(self.files_path_dir)
            mkdir(self.files_path_public)
            mkdir(self.files_path_private)

    def delfile(self, repo='public', filename=None, type="misc"):
        if repo == "public":
            remove(path.join(self.files_path_public, type, filename))
        elif repo == "private":
            remove(path.join(self.files_path_private, type, filename))
        elif repo is None:
            remove(filename)

    def get_ext(self, filename=None):
        return path.splitext(filename)[1]


class Email:
    def __init__(self, user=current_user):
        self.server = SMTP('smtp.gmail.com', 587)
        self.server.connect("smtp.gmail.com", 587)
        self.server.ehlo()
        self.server.starttls()
        self.server.login("syncoappauto@gmail.com", "Ocnys2468@$^*")
        self.from_email = "syncoappauto@gmail.com"
        self.msg = MIMEMultipart('alternative')
        self.username = user.username.title()
        self.to_email = user.email

    def confirmation(self, link=None):
        self.msg['To'] = self.to_email
        self.msg['From'] = self.from_email
        self.msg['Subject'] = "Synco - Confirm your account"
        body_plain = MIMEText('Hey {},\nThanks for creating an account with Synco. \nTo continue with the account '
                              'creation process please click the validation link below to verify your email address.\n'
                              '{}\n\nIf you didn\'t sign up for an account at Synco no further action is required and '
                              'you can safely disregard this message.'.format(self.username, link), 'plain')
        # body_html = MIMEText("", "html")
        self.msg.attach(body_plain)
        # self.msg.attach(body_html)
        self.server.sendmail(self.from_email, self.to_email, self.msg.as_string())

    def pass_reset(self, link=None):
        self.msg['To'] = self.to_email
        self.msg['From'] = self.from_email
        self.msg['Subject'] = "Synco - Password Reset"
        body_plain = MIMEText('Hey {},\nWe have reset the password for the Synco Account associated with this email '
                              'address.\nTo choose a new password, click this link and follow the instructions:\n{}'
                              .format(self.username, link))
        # body_html = MIMEText("", "html")
        self.msg.attach(body_plain)
        # self.msg.attach(body_html)
        self.server.sendmail(self.from_email, self.to_email, self.msg.as_string())


class Tokens:
    def __init__(self, length=20):
        while length > 0:
            self.token = urandom(length)
            self.token = hexlify(self.token).decode()
            if Token.query.filter_by(token=self.token).first() is None:
                break

    def auth(self, token_db=None):
        if token_db is not None:
            return "auth"
        else:
            return "invalid"


class Database:
        def __init__(self, commit=False):
            if commit:
                db.session.commit()

        def add(self, *args):
            for arg in args:
                db.session.add(arg)
                db.session.commit()

        def delete(self, *args):
            for arg in args:
                db.session.delete(arg)
                db.session.commit()


class Action:
    def __init__(self, user=current_user, file=None):
        self.file_path = FilesPath(user=user)
        self.file = file
        if self.file is not None:
            self.id = str(self.file.id)
        self.type_list = ["document", "image", "audio", "video"]

    def download(self):
        if any(self.file.type == type_check for type_check in self.type_list):
            self.id = self.id + self.file_path.get_ext(self.file.filename)
        if self.file.repo == "public":
            if self.file_path.isfile(type=self.file.type, filename=self.id):
                return self.file_path.public(type=self.file.type, filename=self.id)
        elif self.file.repo == "private":
            if self.file_path.isfile(filename=self.id, repo="private", type=self.file.type):
                return self.file_path.private(type=self.file.type, filename=self.id)

    def delete(self):
        if any(self.file.type == type_check for type_check in self.type_list):
            self.id = self.id + self.file_path.get_ext(self.file.filename)
        db = Database()
        if self.file.repo == "public":
            if self.file_path.isfile(filename=self.id, type=self.file.type):
                flash('{} is deleted.'.format(self.file.filename))
                self.file_path.delfile(type=self.file.type, filename=self.id)
                if self.file.type == "misc":
                    db.delete(self.file)
                else:
                    db.delete(self.file.open_file.first(), self.file)
        elif self.file.repo == "private":
            if self.file_path.isfile(filename=self.id, repo="private", type=self.file.type):
                flash('{} is deleted.'.format(self.file.filename))
                self.file_path.delfile(type=self.file.type, filename=self.id, repo="private")
                if self.file.type == "misc":
                    db.delete(self.file)
                else:
                    db.delete(self.file.open_file.first(), self.file)
        return url_for('user', username=current_user.username)
