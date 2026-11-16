"""Gunicorn entry point: gunicorn wsgi:application."""

from addressbook.app import Application

application = Application()
