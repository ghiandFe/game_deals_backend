from django.test import TestCase

from deals.models import Deal, Store


class StoreModelTestCase(TestCase):
    """
    Test to verify the Store model
    """
    def setUp(self):
        Store.objects.create(id=111, name='Foo Game Store')
        Store.objects.create(id=222, name='Bar Game Store')
        return super().setUp()

    def test_store_str(self):
        "Test of the __str__() method"
        store = Store.objects.get(id=111)
        self.assertEqual(store.__str__(), 'Foo Game Store')

    def test_store_internal_name_auto_populate(self):
        "Test of the 'uppercase/white space' convertion"
        store = Store.objects.get(id=111)
        self.assertEqual(store.internal_name, 'FOOGAMESTORE')

    def test_store_get_by_internal_name(self):
        "Test getting a Store by internal_name field"
        self.assertEqual(
            Store.objects.get(internal_name='FOOGAMESTORE').id,
            111
        )
        self.assertEqual(
            Store.objects.get(internal_name='BARGAMESTORE').id,
            222
        )


class DealModelTestCase(TestCase):
    """
    Test to verify the Deal model
    """
    def setUp(self):
        store = Store.objects.create(
            id = 333,
            name = 'Foo Bar Gaming'
        )
        Deal.objects.create(
            id = 'DEAL_1',
            title = 'Awesome Game',
            normal_price = 29.99,
            store = store
        )
        Deal.objects.create(
            id = 'DEAL_2',
            title = 'Bar Game',
            store = store,
            img_url = 'https://cdn.somewhere.com/capsule_sm_120.jpg'
        )
        Deal.objects.create(
            id = 'DEAL_3',
            title = 'Bar Game',
            store = store,
            img_url = 'https://cdn.somewhereelse.com/foo.jpg'
        )
        return super().setUp()

    def test_deal_str(self):
        "Test of the __str__() method"
        deal = Deal.objects.get(id='DEAL_1')
        self.assertEqual(deal.__str__(), 'Awesome Game')

    def test_header_img_field_auto_populate(self):
        "Testing the auto populate of the header_img field"
        deals = Deal.objects.all()
        self.assertIsNone(deals[0].header_img)
        self.assertIn('header', deals[1].header_img)
        self.assertNotIn('header', deals[2].header_img)