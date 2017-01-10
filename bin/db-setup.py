#!/usr/bin/env python
from argparse import ArgumentParser
import subprocess
import os
import django
os.environ['DJANGO_SETTINGS_MODULE'] = 'csa.settings'
django.setup()

from csa.tests.functional import create_test_data # noqa


def test_data():
    create_test_data()

parser = ArgumentParser(description='CSA database setup tool')
parser.add_argument('--drop', action='store_true', help='drop tables')
parser.add_argument('--init', action='store_true', help='creates tables and initialize')
parser.add_argument('--test-data', action='store_true', help='add test data')

args = parser.parse_args()

if args.drop:
    subprocess.check_call(
        'python ./manage.py sqlflush | ./manage.py dbshell',
        shell=True)

if args.init:
    for cmd in [
            'python ./manage.py makemigrations csa --no-input',
            'python ./manage.py migrate --no-input'
    ]:
        subprocess.check_call(cmd, shell=True)

if args.test_data:
    test_data()
