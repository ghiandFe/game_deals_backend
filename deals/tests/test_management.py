from django.core.management import call_command
from django.test import TestCase
from io import StringIO

from deals.management.utils.call_api import call_api
from deals.models import Deal, Store



class CallApiUtilsTestCase(TestCase):
    """
    Test the function utils/call_api
    """

    api_url = 'https://www.cheapshark.com/api/1.0/deals'

    def test_call_api(self):
        "Try to call api url"
        response = call_api(self.api_url)
        self.assertNotIsInstance(response, str)
        self.assertEqual(response.status_code, 200)

    def test_call_api_with_payload(self):
        "Try to call api url with payload"
        payload = { 'pageSize': 16 }
        response = call_api(self.api_url, payload)
        self.assertNotIsInstance(response, str)
        data = response.json()
        self.assertEqual(len(data), 16)

    def test_call_api_invalid_url(self):
        "Verify the error response if url is invalid"
        response = call_api(url='http://fakeurl.testcase.asd')
        self.assertIsInstance(response, str)
        self.assertIn('Call API FAILED', response)


class FetchStoresTestCase(TestCase):
    """
    Test the command 'python manage.py fetch_stores'
    """

    def call_command(self):
        out = StringIO()
        call_command(
            'fetch_stores',
            stdout=out,
            stderr=StringIO()
        )
        return out.getvalue()

    def test_fetch_stores_output(self):
        "Test success reading stdout"
        out = self.call_command()
        self.assertIn('success', out)
        self.assertIn('successfully', out)

    def test_fetch_stores_saving(self):
        "Test if command saves all stores in DB"
        self.call_command()
        stores = Store.objects.all()
        self.assertEqual(len(stores), 3)

    def test_fetch_stores_dont_save_others_stores(self):
        "Test that the command save only required stores"
        self.call_command()
        store = None
        for x in range(2,7):
            try:
                store = Store.objects.get(pk=2)
            except:
                pass
        self.assertIsNone(store)


class FetchDealsTestCase(TestCase):
    """
    Test the command 'python manage.py fetch_deals'
    """

    def call_command(self):
        call_command('fetch_stores', stdout=StringIO())
        out = StringIO()
        call_command(
            'fetch_deals',
            stdout=out,
            stderr=StringIO()
        )
        return out.getvalue()

    def test_fetch_deals_output(self):
        "Test the command success state"
        out = self.call_command()
        self.assertIn('ALL NEW DEALS SAVED', out)
        self.assertIn('...end saving!', out)
        self.assertNotIn('not populated correctly', out)

    def test_fetch_deals_saving(self):
        "Test if command saves all deals in DB"
        self.call_command()
        deals = Deal.objects.all()
        self.assertEqual(len(deals), 16)

    def test_fetch_deals_update(self):
        "Test the update function"
        self.call_command()
        deals = Deal.objects.all()
        first_deal = deals.first()
        price_before = first_deal.sale_price
        first_deal.sale_price = 150
        first_deal.last_change = 100
        first_deal.save()
        out = self.call_command()
        for deal in deals:
            self.assertIn(deal.__str__(), out)
        updated_deal = Deal.objects.get(id=first_deal.id)
        self.assertEqual(price_before, updated_deal.sale_price)