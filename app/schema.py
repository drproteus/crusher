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
    Tag as TagModel,
)


class Tag(DjangoObjectType):
    class Meta:
        model = TagModel


class Taggable:
    tags = graphene.List(Tag)

    def resolve_tags(self, info):
        return self.tags.all()


class Client(DjangoObjectType, Taggable):
    class Meta:
        model = ClientModel

    metadata = generic.GenericScalar()


class Vessel(DjangoObjectType, Taggable):
    class Meta:
        model = VesselModel

    client = graphene.Field(Client)
    metadata = generic.GenericScalar()

    def resolve_client(self, info):
        return self.client


class Request(DjangoObjectType, Taggable):
    class Meta:
        model = RequestModel

    client = graphene.Field(Client)
    metadata = generic.GenericScalar()

    def resolve_client(self, info):
        return self.client


class Job(DjangoObjectType, Taggable):
    class Meta:
        model = JobModel

    vessel = graphene.Field(Vessel)
    origin_request = graphene.Field(Request)
    metadata = generic.GenericScalar()


class SKU(DjangoObjectType, Taggable):
    class Meta:
        model = SKUModel

    metadata = generic.GenericScalar()


class LineItem(DjangoObjectType, Taggable):
    class Meta:
        model = LineItemModel

    sku = graphene.Field(SKU)

    def resolve_sku(self, info):
        return self.sku


class Credit(DjangoObjectType, Taggable):
    class Meta:
        model = CreditModel


class Invoice(DjangoObjectType, Taggable):
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


class TagMutation(graphene.Mutation):
    class Arguments:
        value = graphene.String(required=True)
        object_id = graphene.UUID(required=True)

    tag = graphene.Field(lambda: Tag)

    TAGGABLE_MODELS = (ClientModel, VesselModel, InvoiceModel, SKUModel, JobModel)

    @classmethod
    def mutate(cls, root, info, value, object_id):
        for m in cls.TAGGABLE_MODELS:
            try:
                content_object = m.objects.get(pk=object_id)
                break
            except m.DoesNotExist:
                pass
        else:
            raise Exception("Item not found")
        t = content_object.tags.create(value=value)
        return TagMutation(tag=t)


class UntagMutation(graphene.Mutation):
    class Arguments:
        id = graphene.UUID(required=True)

    ok = graphene.Boolean()

    @classmethod
    def mutate(cls, root, info, id):
        TagModel.objects.filter(pk=id).delete()
        return UntagMutation(ok=True)


class ClientMutation(graphene.Mutation):
    class Arguments:
        company = graphene.String(required=True)
        email = graphene.String()
        mobile = graphene.String()
        mailing_address = graphene.String()
        billing_address = graphene.String()
        tags = graphene.List(graphene.String)
        metadata = generic.GenericScalar(required=False)
        id = graphene.ID()

    client = graphene.Field(lambda: Client)

    @classmethod
    def mutate(
        cls,
        root,
        info,
        company,
        email="",
        mobile="",
        mailing_address="",
        billing_address="",
        tags=None,
        metadata=None,
        id=None,
    ):
        try:
            client = ClientModel.objects.get(pk=id)
            ClientModel.objects.filter(pk=id).update(
                company=company,
                email=email,
                mobile=mobile,
                mailing_address=mailing_address,
                billing_address=billing_address,
                metadata=metadata,
            )
            client = ClientModel.objects.get(pk=id)
        except ClientModel.DoesNotExist:
            client = ClientModel.objects.create(
                company=company,
                email=email,
                mobile=mobile,
                mailing_address=mailing_address,
                billing_address=billing_address,
                metadata=metadata,
            )
        for tag in (tags or []):
            client.tags.create(value=tag)
        return ClientMutation(client=client)


class Mutations(graphene.ObjectType):
    create_client = ClientMutation.Field()
    add_tag = TagMutation.Field()
    remove_tag = UntagMutation.Field()


class Query(graphene.ObjectType):
    invoices = graphene.List(Invoice)
    skus = graphene.List(SKU)
    transport_skus = graphene.List(SKU)
    staff_skus = graphene.List(SKU)
    item_skus = graphene.List(SKU)
    clients = graphene.List(Client)

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

    def resolve_clients(self, info):
        return ClientModel.objects.all()


schema = graphene.Schema(query=Query, mutation=Mutations)
