#!/usr/bin/env python
# -*- coding: utf-8 -*-

__all__ = ["hash_email", "Invitation", "User"]

import os
import flask
from hashlib import sha1
from datetime import datetime
from SimpleAES import SimpleAES
from sqlalchemy import Column, Integer, String, Boolean, DateTime

from .database import db


def hash_email(email):
    return sha1(email).hexdigest()


def encrypt_email(email):
    aes = SimpleAES(flask.current_app.config["AES_KEY"])
    return aes.encrypt(email)


def decrypt_email(enc_email):
    aes = SimpleAES(flask.current_app.config["AES_KEY"])
    return aes.decrypt(enc_email)


class Invitation(db.Model):

    __tablename__ = "invitations"

    id = Column(Integer, primary_key=True)
    email = Column(String)
    code = Column(String)
    sent = Column(Boolean)
    created = Column(DateTime)

    def __init__(self, email, sent=False):
        # Encrypt and hash the email address.
        self.email = hash_email(email)

        # Generate an invitation code.
        self.code = sha1(os.urandom(24)).hexdigest()

        # Invitation sent flag.
        self.sent = sent

        # Date of registration.
        self.created = datetime.utcnow()

    def __repr__(self):
        return "<Invitation(\"{0}\", sent={1})>".format(self.email,
                                                        self.sent)


class User(db.Model):

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)

    email = Column(String)
    hemail = Column(String)
    joined = Column(DateTime)

    openid = Column(String)
    name = Column(String)

    def __init__(self, email, openid, name):
        # Encrypt and hash the email address.
        self.email = encrypt_email(email)
        self.hemail = hash_email(email)

        # Date of registration.
        self.joined = datetime.utcnow()

        # Initialize the OpenID stuff.
        self.openid = openid
        self.name = name

    def __repr__(self):
        return "<User(\"{0}\")>".format(self.get_email())

    def get_email(self):
        return decrypt_email(self.email)

    def get_id(self):
        return self.openid

    def is_authenticated(self):
        return self.openid is not None

    def is_active(self):
        return self.openid is not None

    def is_anonymous(self):
        return False
