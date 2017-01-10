import csa.tests.functional
import csa.orders
import csa.models.core
from freezegun import freeze_time


class CSATests(csa.tests.functional.CSATestCase):
    def testLogin(self):
        client = self.user_client('consumer')
        client.get('/')

    def testCheckout(self):
        consumer = self.user_client('consumer')
        resp = consumer.post(
            '/user/cart/add',
            follow=True,
            data={
                'stock_id': 1,
                'quantity': 1
            })

        self.assertEqual(resp.status_code, 200)

        resp = consumer.post('/user/cart/checkout', follow=True)
        self.assertContains(resp, 'Επιτυχής')

    def testPostDeadlineCheckout(self):
        consumer = self.user_client('consumer')
        resp = consumer.post(
            '/user/cart/add',
            follow=True,
            data={
                'stock_id': 1,
                'quantity': 1
            })

        self.assertEqual(resp.status_code, 200)

        # get deadline
        da = csa.models.core.DeliveryLocation.objects.get(name='Da')
        span = csa.orders.OrdersManager.get_next_deadline(da)
        import pdb; pdb.set_trace()
        # with freeze_time()
