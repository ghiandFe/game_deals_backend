from django.core.management.base import BaseCommand

from deals.management.utils.call_api import call_api
from deals.models import Deal, Store


class Command(BaseCommand):
    help = 'Update DB deals and add others 16 recent deals'

    class Utils:
        api_calls = 0
        stores_names = list(Store.objects.all().values_list('internal_name',
                                                            flat=True))

    def handle(self, *args, **kwargs):
        deals_url = 'https://www.cheapshark.com/api/1.0/deals'
        stores_url = 'https://www.cheapshark.com/api/1.0/stores'
        stores_ids = [1, 7, 11]
        stores_names = []

        self.Utils.api_calls += 1
        response = call_api(url=stores_url)
        if not isinstance(response, str):
            for store in response.json():
                if int(store['storeID']) in stores_ids:
                    stores_names.append(
                        store['storeName'].replace(' ', '').upper()
                    )
        else:
            self.stderr.write(response)

        try:
            assert stores_names == self.Utils.stores_names
        except AssertionError:
            msg =  'The stores are not populated correctly in the DB.\n'
            msg += 'If you haven\'t already, run the "[...] fetch_stores"\n'
            msg += 'command making sure no errors are thrown.\n'
            msg += 'If so, something has probably changed in the external API.'
            self.stdout.write(self.style.WARNING(msg))
        else:
            try:
                old_deals = list(Deal.objects.all())
            except:
                self.stderr.write('Loading data from DB: Undefined error!')
                return
            self._save_new_deals(deals_url)
            self._update_old_deals(deals_url, old_deals)

        return

    def _save_data(self, data: list) -> bool:
        self.stdout.write('Start saving...')
        for el in data:
            self.stdout.write(f'{el["title"]}')

            try:
                store = Store(id=el['storeID'])
            except:
                return False
            deal = Deal(
                id=el['dealID'],
                title = el['title'],
                store = store,
                is_on_sale = el['isOnSale'],
                sale_price = el['salePrice'],
                normal_price = el['normalPrice'],
                savings = el['savings'],
                rating_text = el['steamRatingText'],
                rating_percent = el['steamRatingPercent'],
                rating_count = el['steamRatingCount'],
                release_date = el['releaseDate'],
                last_change = el['lastChange'],
                deal_rating = el['dealRating'],
                img_url = el['thumb']
            )
            try:
                deal.save()
            except:
                return False

        self.stdout.write('...end saving!')
        return True

    def _update_old_deals(self, deals_url, old_deals):
        data = []

        self.stdout.write(f'########## Searching Deals to Update ##########')

        for old_deal in old_deals:
            payload = {
                'storeID': old_deal.store.id,
                'title': old_deal.title,
                'exact': 1
            }

            self.Utils.api_calls += 1
            if self.Utils.api_calls > 30:
                self.Utils.api_calls = 1
                self.stdout.write(self.style.WARNING(
                    'Waiting for API (about 5 minutes)...'
                ))

            response = call_api(deals_url, payload)
            self.stdout.write(f'{old_deal.title}')

            if not isinstance(response, str) and (
                len(json := response.json()) == 1
            ):
                deal_data = json[0]
            else:
                self.stderr.write(response)
                continue

            if (
                old_deal.last_change != deal_data['lastChange']
                and old_deal.id == deal_data['dealID']
            ):
                data.append(deal_data)

        if len(data) > 0:
            self.stdout.write('########## UPDATING OLD DEALS ##########')
            if self._save_data(data):
                self.stdout.write(self.style.SUCCESS(
                    '########## ALL OLD DEALS UPDATED ##########'
                ))
            else:
                self.stderr.write('!!!!!!!!!! UPDATING DEALS ERROR !!!!!!!!!!')
        else:
            self.stdout.write('########## NO DEAL TO UPDATE ##########')

    def _save_new_deals(self, deals_url):
        payload = {
            'storeID[]': ['1', '7', '11'],
            'pageSize': 16,
            'sortBy': 'recent'
        }

        self.Utils.api_calls += 1
        response = call_api(deals_url, payload)

        if not isinstance(response, str):
            self.stdout.write('########## SAVING NEW DEALS ##########')
            if self._save_data(response.json()):
                self.stdout.write(self.style.SUCCESS(
                    '########## ALL NEW DEALS SAVED ##########'
                ))
            else:
                self.stderr.write('!!!!!!!!!! SAVING DEALS ERROR !!!!!!!!!!')
        else:
            self.stderr.write(response)