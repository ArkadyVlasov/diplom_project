from celery import shared_task
from django.core.management import call_command
import requests
import tempfile
import os