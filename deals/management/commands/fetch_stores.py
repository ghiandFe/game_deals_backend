from django.core.management.base import BaseCommand

from deals.management.utils.call_api import call_api
from deals.models import Store


# This command only needs to be run once.
# It MUST be executed BEFORE "fetch_deals"
# (and after DB migration).
class Command(BaseCommand):
    help = 'Save stores into DB'

    class StoreInfo:
        NAMES = {
            1: 'STEAM',
            7: 'GOG',
            11: 'HUMBLESTORE'
        }
        IDS = list(NAMES.keys())

    def handle(self, *args, **kwargs):
        api_url = 'https://www.cheapshark.com/api/1.0/stores'

        response = call_api(url=api_url)
        if not isinstance(response, str):
            self.stdout.write(self.style.SUCCESS(
                f'Call API success! Code: {response.status_code}'
            ))
            self._save_data(response.json())
        else:
            self.stderr.write(response)

        return

    def _save_data(self, data):

        for store in data:
            if (store_id := int(store['storeID'])) in self.StoreInfo.IDS:
                i_name = store['storeName'].replace(' ', '').upper()
                condition = i_name == self.StoreInfo.NAMES[store_id]
                try:
                    assert condition, 'Ops! Something is changed in the API'
                except AssertionError as msg:
                    print(type(msg))
                    self.stderr.write(msg)
                    self.stdout.write(
                        self.style.WARNING(
                            ' ', i_name, '!=', self.StoreInfo.NAMES[store_id]
                        )
                    )
                    continue
                new_store = Store(
                    id = store_id,
                    name = store['storeName'],
                    internal_name = i_name
                )
                new_store.save()
                msg = f'Store {new_store.name} [ID: {new_store.id}] '
                msg += 'successfully saved into DB.'
                self.stdout.write(msg)

        self.stdout.write(self.style.SUCCESS('All stores successfully saved'))
        return