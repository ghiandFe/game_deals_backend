from django.db.models import Q
import graphene
from graphene_django import DjangoObjectType
from graphql_jwt.decorators import login_required

from .models import Deal, Store


class StoreType(DjangoObjectType):
    class Meta:
        model = Store


class DealType(DjangoObjectType):
    class Meta:
        model = Deal


class Query(graphene.ObjectType):
    deal = graphene.Field(DealType, deal_id=graphene.String(required=True))
    deals = graphene.List(DealType,
                          store_id = graphene.Int(),
                          price_lower = graphene.Int(),
                          price_higher = graphene.Int(),
                          order_by = graphene.String(),
                          offset=graphene.Int(),
                          limit=graphene.Int())

    @login_required
    def resolve_deal(self, info, deal_id=None, **kwargs):
        if deal_id:
            return Deal.objects.get(id=deal_id)

    def resolve_deals(self, info,
                      store_id=None, price_lower=None, price_higher=None,
                      order_by='-last_change', offset=None, limit=None, **kwargs):

        queryset = Deal.objects.filter(is_on_sale=True)

        if info.context.user.is_authenticated:
            # FILTERING
            if store_id:
                queryset = queryset.filter(store_id=store_id)

            if not price_lower and price_higher:
                filter = Q(sale_price__lte=price_higher)
                queryset = queryset.filter(filter)
            elif price_lower and price_higher:
                filter = (
                    Q(sale_price__gte=price_lower) &
                    Q(sale_price__lte=price_higher)
                )
                queryset = queryset.filter(filter)
            elif price_lower and not price_higher:
                filter = Q(sale_price__gte=price_lower)
                queryset = queryset.filter(filter)

            # ORDERING
            queryset = queryset.order_by(order_by)

            # PAGINATION
            if offset:
                queryset = queryset[offset:]
            if limit:
                queryset = queryset[:limit]

        # QUERYSET FOR PUBLIC HOME PAGE
        else:
            store_1 = queryset.filter(store_id=1).first()
            store_7 = queryset.filter(store_id=7).first()
            store_11 = queryset.filter(store_id=11).first()
            queryset = [store_1, store_7, store_11]

        return queryset