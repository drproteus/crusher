from graphene_django import DjangoObjectType
import graphene
from graphene.types import generic

from app.metadata import (
    SKUMetadataSchema,
    StaffMetadataSchema,
    TransportMetadataSchema,
    TransportPointSchema,
    VoyagePointSchema,
    ItemMetadataSchema,
)


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


class ModifyClientMutation(graphene.Mutation):
    class Arguments:
        company = graphene.String()
        email = graphene.String()
        mobile = graphene.String()
        mailing_address = graphene.String()
        billing_address = graphene.String()
        metadata = generic.GenericScalar()
        update_fields = graphene.List(graphene.String)
        id = graphene.ID()

    client = graphene.Field(lambda: Client)

    @classmethod
    def mutate(
        cls,
        root,
        info,
        company="",
        email="",
        mobile="",
        mailing_address="",
        billing_address="",
        metadata=None,
        update_fields=None,
        id=None,
    ):
        try:
            client = ClientModel.objects.get(pk=id)
        except ClientModel.DoesNotExist:
            client = ClientModel()
            if not company:
                raise Exception("Company Name required for new Client record")
        client.metadata = metadata or {}
        client.company = company
        client.email = email
        client.mobile = mobile
        client.mailing_address = mailing_address
        client.billing_address = billing_address
        client.save(update_fields=update_fields)
        client = ClientModel.objects.get(pk=client.id)
        return ModifyClientMutation(client=client)


class ModifyVesselMutation(graphene.Mutation):
    class Arguments:
        name = graphene.String()
        client_id = graphene.String()
        mmsi = graphene.String()
        metadata = generic.GenericScalar()
        update_fields = graphene.List(graphene.String)
        id = graphene.ID()

    vessel = graphene.Field(lambda: Vessel)

    @classmethod
    def mutate(
        cls,
        root,
        info,
        name,
        client_id=None,
        mmsi="",
        metadata=None,
        update_fields=None,
        id=None,
    ):
        try:
            vessel = VesselModel.objects.get(pk=id)
        except VesselModel.DoesNotExist:
            vessel = VesselModel()
            if not client_id:
                raise Exception("Vessel must belong to a Client record")
        vessel.metadata = metadata or {}
        vessel.client_id = client_id
        vessel.mmsi = mmsi
        vessel.save(update_fields=update_fields)
        vessel = VesselModel.objects.get(pk=vessel.id)
        return ModifyVesselMutation(vessel=vessel)


class ModifyJobMutation(graphene.Mutation):
    class Arguments:
        vessel_id = graphene.String()
        origin_request_id = graphene.String()
        metadata = generic.GenericScalar()
        id = graphene.ID()

    job = graphene.Field(lambda: Job)

    @classmethod
    def mutate(
        cls, root, info, vessel_id, origin_request_id=None, metadata=None, id=None
    ):
        metadata = metadata or {}
        try:
            JobModel.objects.filter(pk=id).update(
                vessel_id=vessel_id, origin_request_id=origin_request_id, metadata={}
            )
            job = JobModel.objects.get(pk=id)
        except JobModel.DoesNotExist:
            job = JobModel.objects.create(
                vessel_id=vessel_id,
                origin_request_id=origin_request_id,
                metadata=metadata,
            )
        return ModifyJobMutation(job=job)


class SKUArguments:
    id = graphene.ID()
    metadata = generic.GenericScalar()
    name = graphene.String()
    default_price = graphene.Float()
    default_quantity = graphene.Float()
    minimum_price = graphene.Float()
    minimum_quantity = graphene.Float()
    maximum_price = graphene.Float()
    maximum_quantity = graphene.Float()
    units = graphene.String()


class ModifySKUMutation(graphene.Mutation):
    class Arguments(SKUArguments):
        pass

    sku = graphene.Field(SKU)

    @classmethod
    def mutate(cls, root, info, id=None, metadata=None, **sku_kwargs):
        sku_kwargs["metadata"] = SKUMetadataSchema().load(metadata or {})
        try:
            SKUModel.objects.filter(pk=id).update(**sku_kwargs)
            sku = SKUModel.objects.get(pk=id)
        except SKUModel.DoesNotExist:
            sku = SKUModel.objects.create(**sku_kwargs)
        return ModifySKUMutation(sku=sku)


class ModifyItemMutation(graphene.Mutation):
    class Arguments(SKUArguments):
        pass

    item = graphene.Field(SKU)

    @classmethod
    def mutate(cls, root, info, id=None, metadata=None, **sku_kwargs):
        sku_kwargs["metadata"] = ItemMetadataSchema().load(metadata or {})
        try:
            SKUModel.items.filter(pk=id).update(**sku_kwargs)
            sku = SKUModel.items.get(pk=id)
        except SKUModel.DoesNotExist:
            sku = SKUModel.items.create(**sku_kwargs)
        return ModifyItemMutation(item=sku)


class ModifyStaffMutation(graphene.Mutation):
    class Arguments(SKUArguments):
        pass

    staff = graphene.Field(SKU)

    @classmethod
    def mutate(cls, root, info, id=None, metadata=None, **sku_kwargs):
        sku_kwargs["metadata"] = StaffMetadataSchema().load(metadata or {})
        try:
            SKUModel.staff.filter(pk=id).update(**sku_kwargs)
            sku = SKUModel.staff.get(pk=id)
        except SKUModel.DoesNotExist:
            sku = SKUModel.staff.create(**sku_kwargs)
        return ModifyStaffMutation(staff=sku)


class ModifyTransportationMutation(graphene.Mutation):
    class Arguments(SKUArguments):
        pass

    transportation = graphene.Field(SKU)

    @classmethod
    def mutate(cls, root, info, id=None, metadata=None, **sku_kwargs):
        sku_kwargs["metadata"] = TransportMetadataSchema().load(metadata or {})
        try:
            SKUModel.transportation.filter(pk=id).update(**sku_kwargs)
            sku = SKUModel.transportation.get(pk=id)
        except SKUModel.DoesNotExist:
            sku = SKUModel.transportation.create(**sku_kwargs)
        return ModifyTransportationMutation(transportation=sku)


class ModifyInvoiceMutation(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        job_id = graphene.String()
        due_date = graphene.DateTime()
        metadata = generic.GenericScalar()

    invoice = graphene.Field(Invoice)

    @classmethod
    def mutate(
        cls, root, info, id=None, job_id=None, state=0, due_date=None, metadata=None
    ):
        metadata = metadata or {}
        try:
            invoice = InvoiceModel.objects.filter(pk=id).update(
                state=state, due_date=due_date, metadata=metadata
            )
        except InvoiceModel.DoesNotExist:
            invoice = InvoiceModel.objects.create(
                state=state, due_date=due_date, metadate=metadata
            )
        return ModifyInvoiceMutation(invoice=invoice)


class Mutations(graphene.ObjectType):
    modify_client = ModifyClientMutation.Field()
    modify_vessel = ModifyVesselMutation.Field()
    modify_job = ModifyJobMutation.Field()
    modify_sku = ModifySKUMutation.Field()
    modify_item = ModifyItemMutation.Field()
    modify_staff = ModifyStaffMutation.Field()
    modify_transportation = ModifyTransportationMutation.Field()


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
