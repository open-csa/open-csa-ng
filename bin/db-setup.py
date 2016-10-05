#!/usr/bin/env python
from argparse import ArgumentParser
import subprocess
import os
import django
os.environ['DJANGO_SETTINGS_MODULE'] = 'csa.settings'
django.setup()

import csa.models as m  # noqa


def test_data():
    unit_kilo = m.core.ProductMeasureUnit.objects.create(name='κιλό')
    unit_matso = m.core.ProductMeasureUnit.objects.create(name='μάτσο')
    unit_bazaki = m.core.ProductMeasureUnit.objects.create(name='βαζάκι')
    category_laxanika = m.core.ProductCategory.objects.create(name='Λαχανικά')
    category_metapoiimena = m.core.ProductCategory.objects.create(name='Μεταποιημένα')

    da = m.core.DeliveryLocation.objects.create(
        name='Da',
        address='Ντεντιδάκιδων 15',
        delivery_weekday=2,
        delivery_time='17:00',
        delivery_duration=5400,  # 1.5 hours
        orders_deadline_weekday=0,
        orders_deadline_time='18:00')

    password = 'p4ssw0rd'
    admin = m.user.User.objects.create_superuser(
        username='admin',
        email='csa@example.com',
        password=password,
        first_name='CSA',
        last_name='Διαχειρηστής')
    m.user.UserProfile.objects.create(
        user=admin,
        phone_number='+306976823542',
        consumer=m.user.Consumer.objects.create(
            preferred_delivery_location=da
        ))

    consumer = m.user.User.objects.create_user(
        username='consumer',
        email='consumer@example.com',
        password=password,
        first_name='Τάκης',
        last_name='Σουπερμαρκετάκης')
    m.user.UserProfile.objects.create(
        user=consumer,
        phone_number='+306976823542',
        consumer=m.user.Consumer.objects.create(
            preferred_delivery_location=da
        ))

    vasw = m.user.User.objects.create_user(
        username='vasw',
        email='vasw@example.com',
        password=password,
        first_name='Βάσω',
        last_name='Παρασύρη')
    m.user.UserProfile.objects.create(
        user=vasw,
        phone_number='+306976823542',
        producer=m.user.Producer.objects.create(),
        consumer=m.user.Consumer.objects.create(
            preferred_delivery_location=da
        ))

    mixalis = m.user.User.objects.create_user(
        username='mixalis',
        email='mixalis@example.com',
        password=password,
        first_name='Μιχάλης',
        last_name='Μανιαδάκης')
    m.user.UserProfile.objects.create(
        user=mixalis,
        phone_number='+306976823542',
        producer=m.user.Producer.objects.create(),
        consumer=m.user.Consumer.objects.create(
            preferred_delivery_location=da
        ))

    aggouri = m.core.Product.objects.create(
        name='Αγγούρι',
        description='Το αγγούρι είναι καρπός που προέρχεται από το έρπον και '
        'αναρριχώμενο ετήσιο φυτό της αγγουριάς Cucumis sativus-Σικυός ο '
        'ήμερος. Ανήκει στην οικογένεια (βιολογία) κολοκυνθοειδών όπως το πεπόνι, '
        'το καρπούζι, το κολοκύθι. Η αγγουριά καλλιεργείται στην ύπαιθρο τους '
        'καλοκαιρινούς μήνες και σε θερμοκήπιο τον υπόλοιπο χρόνο, λόγω της '
        'ευαισθησίας στις χαμηλές θερμοκρασίες. Η υψηλή θερμοκρασία και υγρασία '
        'ευνοούν την ανάπτυξή της.',
        unit=unit_kilo)
    aggouri.categories.add(category_laxanika)

    aggouri_vasw = m.core.ProductStock.objects.create(
        product=aggouri,
        producer=vasw,
        variety='Κλωσσούδι',
        description='Τα λεγόμενα αγγουράκια της Βάσως',
        is_available=True,
        is_stockable=False,
        quantity=0,
        price=150)
    aggouri_vasw.supported_delivery_locations.add(da)


    marmelada = m.core.Product.objects.create(
        name='Μαρμελάδα',
        description='Η μαρμελάδα... τι να πρωτογράψει κανείς; Αυτό το αρχαίο γλυκό '
                    'πασάλημα ψωμιού έχει κλέψει τις καρδιές και τους στοματικούς μας '
                    'κάλυκες εδώ και χιλιάδες χρόνια. Ακόμα και αυτή τη στιγμή ανακαλύπτονται '
                    'σε ανασκαφές αρχαίων τάφων βαζάκια διαφόρων ειδών μαρμαλάδες. '
                    'Πέρα από την επάλυψη σε ζεστές φέτες ψωμιού το θεσπέσιο αυτό γλύκισμα '
                    'χρησιμοποιείται στη παρασκευή του αγαπημένου σε όλους γλυκό πάστα φλώρα!',
        unit=unit_bazaki)
    marmelada.categories.add(category_metapoiimena)

    marmelada_vasw = m.core.ProductStock.objects.create(
        product=marmelada,
        producer=mixalis,
        variety='Φράουλα',
        description='Τόσο γλυκιά που θα σας πέσουνε τα δόντια',
        is_available=True,
        is_stockable=True,
        quantity=8,
        price=300)
    marmelada_vasw.supported_delivery_locations.add(da)

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
