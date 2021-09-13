from django.contrib.auth import get_user_model
from graphene_django.utils.testing import GraphQLTestCase
from graphql_jwt.shortcuts import get_token
from json import loads as jsonLoads

from deals.models import Deal, Store


def mainSetUp():
    store1 = Store.objects.create(
        id = 1,
        name = 'Steam'
    )
    store7 = Store.objects.create(
        id = 7,
        name = 'GOG'
    )
    for x in range(5):
        Deal.objects.create(
            id = f'DEALTESTID_{x+1}',
            title = f'MYSIMPLEDEAL_{x+1}',
            sale_price = 2.99 + x,
            savings = 70.0 + (x*5),
            deal_rating = 8.2 - (x*0.5),
            store = store1
        )
    Deal.objects.create(
        id = "GOG_1",
        title = "GOG GAME",
        sale_price = 12.49,
        savings = 65.00,
        deal_rating = 8.7,
        store = store7
    )


class DealAPINoAuthTestCase(GraphQLTestCase):
    """
    API test - anonymous users
    """

    def setUp(self) -> None:
        mainSetUp()
        return super().setUp()

    def test_schema_resolve_deals_no_auth(self):
        """
        Test if method resolve_deals() return only 3 deals
        if user is not authenticated.
        store_id = 11 not exists, so deals array must be [Deal, Deal, None]
        """
        response = self.query(
            '''
            query {
                deals {
                    id
                    store {
                        id
                    }
                }
            }
            '''
        )
        self.assertResponseNoErrors(response)
        deals = jsonLoads(response.content)['data']['deals']

        self.assertEqual(len(deals), 3)
        self.assertIsNotNone(deals[0])
        self.assertIsNotNone(deals[1])
        self.assertIsNone(deals[2])
        self.assertEqual(deals[0]['id'], 'DEALTESTID_1')
        self.assertEqual(deals[1]['id'], 'GOG_1')
        self.assertEqual(deals[0]['store']['id'], 1)
        self.assertEqual(deals[1]['store']['id'], 7)


class DealAPIAuthTestCase(GraphQLTestCase):
    """
    API test - authenticated users
    """

    USER = get_user_model()

    def setUp(self) -> None:
        mainSetUp()
        user = self.USER(
            username='federico'
        )
        user.set_password('sup3rSecret_password')
        user.save()
        return super().setUp()

    def _fetchDeals(self, variables=None) -> list:
        user = self.USER.objects.get(id=1)
        token = get_token(user)
        headers = {
            'HTTP_AUTHORIZATION': f'GDjwt {token}'
        }
        query = '''
                query deals(
                    $storeId: Int
                    $priceLower: Int
                    $priceHigher: Int
                    $orderBy: String
                    $offset: Int
                    $limit: Int
                ) {
                    deals(
                    storeId: $storeId
                    priceLower: $priceLower
                    priceHigher: $priceHigher
                    orderBy: $orderBy
                    offset: $offset
                    limit: $limit
                    ) {
                        id
                        title
                        salePrice
                        savings
                        dealRating
                        store {
                            id
                        }
                    }
                }
                '''
        response = self.query(query, variables=variables, headers=headers)
        self.assertResponseNoErrors(response)
        return jsonLoads(response.content)['data']['deals']

    def _dict_to_number(self, deals, field) -> list:
        return [deal[field] for deal in deals]

    def test_schema_resolve_deals_auth_user(self):
        """
        Test if method resolve_deals() return all deals
        if user is authenticated.
        """

        deals = self._fetchDeals()

        self.assertEqual(len(deals), 6)
        deal = deals[2]
        self.assertIsInstance(deal, dict)
        self.assertIsInstance(deal['salePrice'], float)
        self.assertEqual(deal['title'], 'MYSIMPLEDEAL_3')
        self.assertEqual(deal['store']['id'], 1)

    def test_store_filter_query(self):
        "Test filter 'storeId'"
        deals = self._fetchDeals(variables={
            'storeId': 7
        })
        self.assertEqual(len(deals), 1)
        self.assertEqual(deals[0]['store']['id'], 7)

    def test_price_filter_query(self):
        "Test filter 'price'"
        deals = self._fetchDeals(variables={
            'priceLower': 3,
            'priceHigher': 6
        })
        self.assertEqual(len(deals), 3)
        prices = []
        for deal in deals:
            prices.append(deal['salePrice'])
        self.assertTrue(min(prices) > 3)
        self.assertTrue(max(prices) < 6)

    def test_sort_deals_query(self):
        "Test deals sorting"
        sort = [None, 'sale_price', '-savings', '-deal_rating']
        deals = []
        for x in sort:
            deals.append(self._fetchDeals(variables={
                'orderBy': x
            }))
        default, price, savings, rating = deals
        # Ordering by "None" returns default order
        self.assertListEqual(default, price)

        price_list = self._dict_to_number(price, 'salePrice')
        sav_list = self._dict_to_number(savings, 'savings')
        rate_list = self._dict_to_number(rating, 'dealRating')

        self.assertEqual(min(price_list), price_list[0])
        self.assertEqual(max(price_list), price_list[5])
        self.assertEqual(min(sav_list), sav_list[5])
        self.assertEqual(max(sav_list), sav_list[0])
        self.assertEqual(min(rate_list), rate_list[5])
        self.assertEqual(max(rate_list), rate_list[0])

    def test_pagination_query(self):
        "Test deals pagination"
        offset = 0
        per_page = 2
        while True:
            deals = self._fetchDeals(variables={
                'offset': offset,
                'limit': per_page
            })
            try:
                self.assertEqual(len(deals), 2)
            except AssertionError:
                break
            offset += per_page
        self.assertEqual(offset, 6)

    def test_filters_sort_pag_query(self):
        "Test with all filter and sort variables"
        offset = 0
        per_page = 3
        while True:
            deals = self._fetchDeals(variables={
                'storeId': 1,
                'priceLower': 1,
                'priceHigher': 6,
                'orderBy': '-savings',
                'offset': offset,
                'limit': per_page
            })
            for deal in deals:
                self.assertEqual(deal['store']['id'], 1)
            prices = self._dict_to_number(deals, 'salePrice')
            self.assertTrue(min(prices) > 1)
            self.assertTrue(max(prices) < 6)
            try:
                self.assertEqual(len(deals), 3)
            except AssertionError:
                self.assertEqual(len(deals), 1)
                break
            self.assertTrue(deals[0]['savings'] > deals[1]['savings'])
            offset += per_page


