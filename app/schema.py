from graphene_django import DjangoObjectType
import graphene
from graphene.types import generic

from app.metadata import (
    SKUMetadataSchema,
    ServiceMetadataSchema,
    TransportMetadataSchema,
    TransportPointSchema,
    VoyagePointSchema,
    ItemMetadataSchema,
)


from app.models import (
    Contact as ContactModel,
    Invoice as InvoiceModel,
    LineItem as LineItemModel,
    Credit as CreditModel,
    SKU as SKUModel,
    Client as ClientModel,
    Vessel as VesselModel,
    Request as RequestModel,
    Job as JobModel,
    ItemSKU as ItemSKUModel,
    ServiceSKU as ServiceSKUModel,
    TransportationSKU as TransportationSKUModel,
)


class Contact(DjangoObjectType):
    class Meta:
        model = ContactModel

    metadata = generic.GenericScalar()
    name = graphene.String()
    fullname = graphene.String()

    def resolve_name(self, info):
        return self.name

    def resolve_fullname(self, info):
        return self.fullname


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


class ModifyContactMutation(graphene.Mutation):
    class Arguments:
        first_name = graphene.String()
        last_name = graphene.String()
        title = graphene.String()
        role = graphene.String()
        primary_email = graphene.String()
        phone_number = graphene.String()
        mailing_address = graphene.String()
        billing_address = graphene.String()
        metadata = generic.GenericScalar()
        update_fields = graphene.List(graphene.String)
        id = graphene.ID()

    contact = graphene.Field(lambda: Contact)

    @classmethod
    def mutate(
        cls,
        root,
        info,
        first_name=None,
        last_name=None,
        title=None,
        role=None,
        primary_email=None,
        phone_number=None,
        mailing_address=None,
        billing_address=None,
        metadata=None,
        update_fields=None,
        id=None,
    ):
        try:
            contact = ContactModel.objects.get(pk=id)
        except ContactModel.DoesNotExist:
            contact = ContactModel()
        contact.first_name = first_name
        contact.last_name = last_name
        contact.title = title
        contact.role = role
        contact.primary_email = primary_email
        contact.phone_number = phone_number
        contact.mailing_address = mailing_address
        contact.billing_address = billing_address
        contact.metadata = metadata or {}
        contact.save(update_fields=update_fields)
        return ModifyContactMutation(contact=contact)


class ModifyClientConnectionMutation(graphene.Mutation):
    class Arguments:
        c1_id = graphene.ID(required=True)
        c2_id = graphene.ID(required=True)
        action = graphene.String()

    ok = graphene.Boolean()

    @classmethod
    def mutate(cls, root, info, c1_id, c2_id, action="link"):
        c1 = ContactModel.objects.get(pk=c1_id)
        c2 = ContactModel.objects.get(pk=c2_id)
        if action == "link":
            c1.connections.add(c2)
            return ModifyClientConnectionMutation(ok=True)
        elif action == "unlink":
            c1.connections.remove(c2)
            return ModifyClientConnectionMutation(ok=True)
        return ModifyClientConnectionMutation(ok=False)


class ModifyClientMutation(graphene.Mutation):
    class Arguments:
        company = graphene.String()
        contact_id = graphene.ID()
        metadata = generic.GenericScalar()
        update_fields = graphene.List(graphene.String)
        id = graphene.ID()

    client = graphene.Field(lambda: Client)

    @classmethod
    def mutate(
        cls,
        root,
        info,
        company=None,
        contact_id=None,
        metadata=None,
        update_fields=None,
        id=None,
    ):
        try:
            client = ClientModel.objects.get(pk=id)
        except ClientModel.DoesNotExist:
            client = ClientModel(contact_id=contact_id)
            if not company:
                raise Exception("Company Name required for new Client record")
        client.metadata = metadata or {}
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


class ModifySKURelationMutation(graphene.Mutation):
    class Arguments:
        s1_id = graphene.UUID(required=True)
        s2_id = graphene.UUID(required=True)
        action = graphene.String()

    ok = graphene.Boolean()

    @classmethod
    def mutate(cls, root, info, s1_id, s2_id, action="link"):
        s1 = SKUModel.objects.get(pk=s1_id)
        s2 = SKUModel.objects.get(pk=s2_id)
        if action == "link":
            s1.related_skus.add(s2)
            return ModifySKURelationMutation(ok=True)
        elif action == "unlink":
            s1.related_skus.remove(s2)
            return ModifySKURelationMutation(ok=True)
        return ModifySKURelationMutation(ok=False)


class ModifySKUContactRelationMutation(graphene.Mutation):
    class Arguments:
        contact_id = graphene.UUID(required=True)
        sku_id = graphene.UUID(required=True)
        action = graphene.String()

    ok = graphene.Boolean()

    @classmethod
    def mutate(cls, root, info, contact_id, sku_id, action="link"):
        contact = ContactModel.objects.get(pk=contact_id)
        sku = SKUModel.objects.get(pk=sku_id)
        if action == "link":
            contact.skus.add(sku)
            return ModifySKUContactRelationMutation(ok=True)
        elif action == "unlink":
            contact.skus.remove(sku)
            sku.contacts.remove(contact)
            return ModifySKUContactRelationMutation(ok=True)
        return ModifySKUContactRelationMutation(ok=False)


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
    def mutate(cls, root, info, id=None, **sku_kwargs):
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
    def mutate(cls, root, info, id=None, **sku_kwargs):
        try:
            SKUModel.items.filter(pk=id).update(**sku_kwargs)
            sku = SKUModel.items.get(pk=id)
        except SKUModel.DoesNotExist:
            sku = SKUModel.items.create(**sku_kwargs)
        return ModifyItemMutation(item=sku)


class ModifyServiceMutation(graphene.Mutation):
    class Arguments(SKUArguments):
        pass

    staff = graphene.Field(SKU)

    @classmethod
    def mutate(cls, root, info, id=None, **sku_kwargs):
        try:
            SKUModel.staff.filter(pk=id).update(**sku_kwargs)
            sku = SKUModel.staff.get(pk=id)
        except SKUModel.DoesNotExist:
            sku = SKUModel.staff.create(**sku_kwargs)
        return ModifyServiceMutation(staff=sku)


class ModifyTransportationMutation(graphene.Mutation):
    class Arguments(SKUArguments):
        pass

    transportation = graphene.Field(SKU)

    @classmethod
    def mutate(cls, root, info, id=None, **sku_kwargs):
        try:
            SKUModel.transportation.filter(pk=id).update(**sku_kwargs)
            sku = SKUModel.transportation.get(pk=id)
        except SKUModel.DoesNotExist:
            sku = SKUModel.transportation.create(**sku_kwargs)
        return ModifyTransportationMutation(transportation=sku)


class BeginInvoiceMutation(graphene.Mutation):
    class Arguments:
        job_id = graphene.String()
        due_date = graphene.DateTime()
        metadata = generic.GenericScalar()

    invoice = graphene.Field(Invoice)

    @classmethod
    def mutate(cls, root, info, job_id=None, due_date=None, metadata=None):
        metadata = metadata or {}
        invoice = InvoiceModel.objects.create(
            due_date=due_date, metadate=metadata, job_id=job_id
        )
        return BeginInvoiceMutation(invoice=invoice)


class SetInvoiceStateMutation(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        state = graphene.Int(required=True)

    invoice = graphene.Field(Invoice)

    @classmethod
    def mutate(cls, root, info, id, state):
        invoice = Invoice.models.get(pk=id)
        invoice.state = state
        invoice.save()
        return SetInvoiceStateMutation(invoice=invoice)


class SetInvoiceMetadataMutation(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        metadata = generic.GenericScalar(required=True)

    invoice = graphene.Field(Invoice)

    @classmethod
    def mutate(cls, root, info, id, metadata):
        invoice = Invoice.models.get(pk=id)
        invoice.metadata = metadata
        invoice.save()
        return SetInvoiceMetadataMutation(invoice=invoice)


class AddLineItemMutation(graphene.Mutation):
    class Arguments:
        invoice_id = graphene.ID(required=True)
        sku_id = graphene.String(required=True)
        price = graphene.Float()
        quantity = graphene.Float()

    line_item = graphene.Field(LineItem)

    @classmethod
    def mutate(cls, root, info, invoice_id, sku_id, price=None, quantity=None):
        li_kwargs = {}
        if price:
            li_kwargs["price"] = price
        if quantity:
            li_kwargs["quantity"] = quantity
        invoice = InvoiceModel.objects.get(pk=invoice_id)
        sku = SKU.objects.get(pk=sku_id)
        sku.add_to_invoice(invoice, **li_kwargs)
        invoice.update_balances()
        return AddLineItemMutation(invoice=invoice)


class DeleteLineItemMutation(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    invoice = graphene.Field(Invoice)

    @classmethod
    def mutate(cls, root, info, id):
        li = LineItemModel.objects.get(pk=id)
        invoice_id = li.invoice.id
        invoice = InvoiceModel.objects.get(pk=invoice_id)
        li.delete()
        invoice.update_balances()
        return DeleteLineItemMutation(invoice=invoice)


class ApplyCreditMutation(graphene.Mutation):
    class Arguments:
        invoice_id = graphene.ID(required=True)
        amount = graphene.Float(required=True)
        memo = graphene.String()
        line_item_id = graphene.String()

    credit = graphene.Field(Credit)

    @classmethod
    def mutate(cls, root, info, invoice_id, amount, memo="", line_item_id=None):
        invoice = InvoiceModel.objects.get(pk=invoice_id)
        credit = invoice.credits.create(
            amount=amount, memo=memo, line_item_id=line_item_id
        )
        invoice.update_balances()
        return ApplyCreditMutation(credit=credit)


class DeleteCreditMutation(graphene.Mutation):
    class Arguments:
        credit_id = graphene.ID(required=True)

    invoice = graphene.Field(Invoice)

    @classmethod
    def mutate(cls, root, info, credit_id):
        credit = CreditModel.objects.get(pk=credit_id)
        invoice_id = credit.invoice.id
        credit.delete()
        invoice = InvoiceModel.objects.get(pk=invoice_id)
        invoice.update_balances()
        return DeleteCreditMutation(invoice=invoice)


class GenerateInvoicePreviewMutation(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    url = graphene.String()

    @classmethod
    def mutate(cls, root, info, id):
        # do some rendering junk, upload it, and return a link
        invoice = InvoiceModel.objects.get(pk=id)
        return GenerateInvoicePreviewMutation(url=f"/INVOICE-{invoice.id}.pdf")


class Mutations(graphene.ObjectType):
    modify_contact = ModifyContactMutation.Field()
    modify_contact_connection = ModifyClientConnectionMutation.Field()
    modify_sku_relation = ModifySKURelationMutation.Field()
    modify_sku_contact_relation = ModifySKUContactRelationMutation.Field()
    modify_client = ModifyClientMutation.Field()
    modify_vessel = ModifyVesselMutation.Field()
    modify_job = ModifyJobMutation.Field()
    modify_sku = ModifySKUMutation.Field()
    modify_item = ModifyItemMutation.Field()
    modify_service = ModifyServiceMutation.Field()
    modify_transportation = ModifyTransportationMutation.Field()

    begin_invoice = BeginInvoiceMutation.Field()
    set_invoice_state = SetInvoiceStateMutation.Field()
    set_invoice_metadata = SetInvoiceMetadataMutation.Field()
    get_invoice_pdf_preview = GenerateInvoicePreviewMutation.Field()

    add_line_item = AddLineItemMutation.Field()
    delete_line_item = DeleteLineItemMutation.Field()

    apply_credit = ApplyCreditMutation.Field()
    delete_credit = DeleteCreditMutation.Field()


class Query(graphene.ObjectType):
    invoices = graphene.List(Invoice)
    skus = graphene.List(SKU)
    transport_skus = graphene.List(SKU)
    service_skus = graphene.List(SKU)
    item_skus = graphene.List(SKU)
    clients = graphene.List(Client)
    contacts = graphene.List(Contact)

    def resolve_invoices(self, info):
        return InvoiceModel.objects.all()

    def resolve_skus(self, info):
        return SKUModel.objects.all()

    def resolve_transport_skus(self, info):
        return TransportationSKUModel.objects.all()

    def resolve_service_skus(self, info):
        return ServiceSKUModel.objects.all()

    def resolve_item_skus(self, info):
        return ItemSKUModel.objects.all()

    def resolve_clients(self, info):
        return ClientModel.objects.all()

    def resolve_contacts(self, info):
        return ContactModel.objects.all()


schema = graphene.Schema(query=Query, mutation=Mutations)
