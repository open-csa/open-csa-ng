import django.test
import csa.models as m


class CSATestCase(django.test.TestCase):
    @classmethod
    def setUpTestData(cls):
        create_test_data()

    def user_client(self, username, password='p4ssw0rd'):
        client = django.test.Client()
        client.login(username=username, password=password)
        return client


def create_test_data():
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
        unit=m.core.Product.UNIT_WEIGHT)
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
        unit=m.core.Product.UNIT_WEIGHT)
    marmelada.categories.add(category_metapoiimena)

    marmelada_vasw = m.core.ProductStock.objects.create(
        product=marmelada,
        producer=mixalis,
        variety='Φράουλα',
        description='Τόσο γλυκιά που θα σας πέσουνε τα δόντια',
        is_available=True,
        is_stockable=True,
        quantity=8,
        price=300,
        min_quantity=0.5)
    marmelada_vasw.supported_delivery_locations.add(da)

    m.core.AvailableQuantity.objects.bulk_create([
        m.core.AvailableQuantity(product_stock=marmelada_vasw, quantity=0.5),
        m.core.AvailableQuantity(product_stock=marmelada_vasw, quantity=1)
    ])
