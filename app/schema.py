from graphene_django import DjangoObjectType
import graphene

from app.models import (
    Invoice as InvoiceModel,
    LineItem as LineItemModel,
    Credit as CreditModel,
    SKU as SKUModel,
    Client as ClientModel,
    Staff as StaffModel,
    Item as ItemModel,
)


class Client(DjangoObjectType):
    class Meta:
        model = ClientModel


class Staff(DjangoObjectType):
    class Meta:
        model = StaffModel

    name = graphene.String()

    def resolve_name(self, info):
        return self.name


class Item(DjangoObjectType):
    class Meta:
        model = ItemModel


class SKU(DjangoObjectType):
    class Meta:
        model = SKUModel


class LineItem(DjangoObjectType):
    class Meta:
        model = LineItemModel

    sku = graphene.Field(SKU)

    def resolve_sku(self, info):
        return self.sku


class Credit(DjangoObjectType):
    class Meta:
        model = CreditModel


class Invoice(DjangoObjectType):
    class Meta:
        model = InvoiceModel

    line_items = graphene.List(LineItem)
    credits = graphene.List(Credit)
    client = graphene.Field(Client)

    def resolve_client(self, info):
        return self.client

    def resolve_line_items(self, info):
        return self.line_items.all()

    def resolve_credits(self, info):
        return self.credits.all()


class Query(graphene.ObjectType):
    invoices = graphene.List(Invoice)

    def resolve_invoices(self, info):
        return InvoiceModel.objects.all()


schema = graphene.Schema(query=Query)
