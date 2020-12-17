from graphene_django import DjangoObjectType
import graphene
from graphene.types import generic


from app.models import (
    Invoice as InvoiceModel,
    LineItem as LineItemModel,
    Credit as CreditModel,
    SKU as SKUModel,
    Client as ClientModel,
    Vessel as VesselModel,
    Request as RequestModel,
    Job as JobModel,
)


class Client(DjangoObjectType):
    class Meta:
        model = ClientModel

    metadata = generic.GenericScalar()


class Vessel(DjangoObjectType):
    class Meta:
        model = VesselModel

    client = graphene.Field(Client)
    metadata = generic.GenericScalar()

    def resolve_client(self, info):
        return self.client


class Request(DjangoObjectType):
    class Meta:
        model = RequestModel

    client = graphene.Field(Client)
    metadata = generic.GenericScalar()

    def resolve_client(self, info):
        return self.client


class Job(DjangoObjectType):
    class Meta:
        model = JobModel

    vessel = graphene.Field(Vessel)
    origin_request = graphene.Field(Request)
    metadata = generic.GenericScalar()


class SKU(DjangoObjectType):
    class Meta:
        model = SKUModel

    metadata = generic.GenericScalar()


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

    job = graphene.Field(Job)

    transportation = graphene.List(LineItem)
    staff = graphene.List(LineItem)
    items = graphene.List(LineItem)

    def resolve_client(self, info):
        return self.client

    def resolve_job(self, info):
        return self.job

    def resolve_line_items(self, info):
        return self.line_items.all()

    def resolve_credits(self, info):
        return self.credits.all()

    def resolve_transportation(self, info):
        return self.line_items.filter(sku__metadata__type="transport")

    def resolve_staff(self, info):
        return self.line_items.filter(sku__metadata__type="staff")

    def resolve_item(self, info):
        return self.line_items.filter(sku__metadata__type="item")


class ClientMutation(graphene.Mutation):
    class Arguments:
        company = graphene.String(required=True)
        metadata = generic.GenericScalar(required=False)

    client = graphene.Field(lambda: Client)

    @classmethod
    def mutate(cls, root, info, company, metadata=None):
        client = ClientModel.objects.create(company=company, metadata=metadata)
        return ClientMutation(client=client)


class Mutations(graphene.ObjectType):
    create_client = ClientMutation.Field()


class Query(graphene.ObjectType):
    invoices = graphene.List(Invoice)
    skus = graphene.List(SKU)
    transport_skus = graphene.List(SKU)
    staff_skus = graphene.List(SKU)
    item_skus = graphene.List(SKU)

    def resolve_invoices(self, info):
        return InvoiceModel.objects.all()

    def resolve_skus(self, info):
        return SKUModel.objects.all()

    def resolve_transport_skus(self, info):
        return SKUModel.transportation.all()

    def resolve_staff_skus(self, info):
        return SKUModel.staff.all()

    def resolve_item_skus(self, info):
        return SKUModel.items.all()


schema = graphene.Schema(query=Query, mutation=Mutations)
