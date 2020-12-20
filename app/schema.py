from graphene_django import DjangoObjectType
import graphene
from graphene import relay
from graphene.types import generic
from graphene_django.filter import DjangoFilterConnectionField
import django_filters

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
    Task as TaskModel,
    Job as JobModel,
    ItemSKU as ItemSKUModel,
    ServiceSKU as ServiceSKUModel,
    TransportationSKU as TransportationSKUModel,
    Attachment as AttachmentModel,
)

class Attachment(DjangoObjectType):
    class Meta:
        model = AttachmentModel

    metadata = generic.GenericScalar()
    url = graphene.String()

    def resolve_url(self, info):
        return self.attached_file.url


class Contact(DjangoObjectType):
    class Meta:
        model = ContactModel

    metadata = generic.GenericScalar()
    name = graphene.String()
    fullname = graphene.String()
    image_url = graphene.String()
    attachments = graphene.List(Attachment)

    def resolve_name(self, info):
        return self.name

    def resolve_fullname(self, info):
        return self.fullname

    def resolve_image_url(self, info):
        if not self.image:
            return ""
        return self.image.url

    def resolve_attachments(self, info):
        return self.attachments.all()


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


class Task(DjangoObjectType):
    class Meta:
        model = TaskModel

    client = graphene.Field(Client)
    metadata = generic.GenericScalar()

    def resolve_client(self, info):
        return self.client


class Job(DjangoObjectType):
    class Meta:
        model = JobModel

    vessel = graphene.Field(Vessel)
    origin_task = graphene.Field(Task)
    metadata = generic.GenericScalar()


class SKU(DjangoObjectType):
    class Meta:
        model = SKUModel

    metadata = generic.GenericScalar()


class ServiceSKU(DjangoObjectType):
    class Meta:
        model = ServiceSKUModel

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
    services = graphene.List(LineItem)
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

    def resolve_services(self, info):
        return self.line_items.filter(sku__metadata__type="service")

    def resolve_items(self, info):
        return self.line_items.filter(sku__metadata__type="item")


class ContactInput(graphene.InputObjectType):
    first_name = graphene.String()
    last_name = graphene.String()
    title = graphene.String()
    role = graphene.String()
    primary_email = graphene.String()
    phone_number = graphene.String()
    mailing_address = graphene.String()
    billing_address = graphene.String()
    metadata = generic.GenericScalar()


class ModifyContactMutation(graphene.Mutation):
    class Arguments:
        data = ContactInput(required=True)
        uid = graphene.ID()

    contact = graphene.Field(lambda: Contact)

    @classmethod
    def mutate(
        cls,
        root,
        info,
        data,
        uid=None,
    ):
        try:
            contact = ContactModel.objects.get(pk=uid)
        except ContactModel.DoesNotExist:
            contact = ContactModel()
        for k, v in data.items():
            if v is not None:
                setattr(contact, k, v)
        contact.save()
        return ModifyContactMutation(contact=contact)


class ModifyClientConnectionMutation(graphene.Mutation):
    class Arguments:
        c1_uid = graphene.ID(required=True)
        c2_uid = graphene.ID(required=True)
        action = graphene.String()

    ok = graphene.Boolean()

    @classmethod
    def mutate(cls, root, info, c1_uid, c2_uid, action="link"):
        c1 = ContactModel.objects.get(pk=c1_uid)
        c2 = ContactModel.objects.get(pk=c2_uid)
        if action == "link":
            c1.connections.add(c2)
            return ModifyClientConnectionMutation(ok=True)
        elif action == "unlink":
            c1.connections.remove(c2)
            return ModifyClientConnectionMutation(ok=True)
        return ModifyClientConnectionMutation(ok=False)


class ClientInput(graphene.InputObjectType):
    company = graphene.String()
    contact_uid = graphene.ID()
    metadata = generic.GenericScalar()


class DeleteClientContact(graphene.Mutation):
    class Arguments:
        uid = graphene.ID(required=True)

    client = graphene.Field(lambda: Client)

    @classmethod
    def mutate(cls, root, info, uid):
        client = ClientModel.objects.get(pk=uid)
        client.contact_uid = None
        client.save()
        return DeleteClientContact(client=client)


class ModifyClientMutation(graphene.Mutation):
    class Arguments:
        data = ClientInput(required=True)
        uid = graphene.ID()

    client = graphene.Field(lambda: Client)

    @classmethod
    def mutate(
        cls,
        root,
        info,
        data,
        uid=None,
    ):
        try:
            client = ClientModel.objects.get(pk=uid)
        except ClientModel.DoesNotExist:
            client = ClientModel()
        for k, v in data.items():
            if v is not None:
                setattr(client, k, v)
        client.save()
        return ModifyClientMutation(client=client)


class VesselInput(graphene.InputObjectType):
    name = graphene.String()
    client_uid = graphene.String()
    mmsi = graphene.String()
    metadata = generic.GenericScalar()


class ModifyVesselMutation(graphene.Mutation):
    class Arguments:
        data = VesselInput(required=True)
        uid = graphene.ID()

    vessel = graphene.Field(lambda: Vessel)

    @classmethod
    def mutate(
        cls,
        root,
        info,
        data,
        uid=None,
    ):
        try:
            vessel = VesselModel.objects.get(pk=uid)
        except VesselModel.DoesNotExist:
            vessel = VesselModel()
        for k, v in data.items():
            if v is not None:
                setattr(vessel, k, v)
        vessel.save()
        return ModifyVesselMutation(vessel=vessel)


class JobInput(graphene.InputObjectType):
    vessel_uid = graphene.String()
    origin_task_uid = graphene.String()
    metadata = generic.GenericScalar()


class ModifyJobMutation(graphene.Mutation):
    class Arguments:
        data = JobInput(required=True)
        uid = graphene.ID()

    job = graphene.Field(lambda: Job)

    @classmethod
    def mutate(cls, root, info, data, uid=None):
        try:
            job = JobModel.objects.get(pk=uid)
        except JobModel.DoesNotExist:
            job = JobModel()
        for k, v in data.items():
            if v is not None:
                setattr(job, k, v)
        return ModifyJobMutation(job=job)


class ModifySKURelationMutation(graphene.Mutation):
    class Arguments:
        s1_uid = graphene.UUID(required=True)
        s2_uid = graphene.UUID(required=True)
        action = graphene.String()

    ok = graphene.Boolean()

    @classmethod
    def mutate(cls, root, info, s1_uid, s2_uid, action="link"):
        s1 = SKUModel.objects.get(pk=s1_uid)
        s2 = SKUModel.objects.get(pk=s2_uid)
        if action == "link":
            s1.related_skus.add(s2)
            return ModifySKURelationMutation(ok=True)
        elif action == "unlink":
            s1.related_skus.remove(s2)
            return ModifySKURelationMutation(ok=True)
        return ModifySKURelationMutation(ok=False)


class ModifySKUContactRelationMutation(graphene.Mutation):
    class Arguments:
        contact_uid = graphene.UUID(required=True)
        sku_uid = graphene.UUID(required=True)
        action = graphene.String()

    ok = graphene.Boolean()

    @classmethod
    def mutate(cls, root, info, contact_uid, sku_uid, action="link"):
        contact = ContactModel.objects.get(pk=contact_uid)
        sku = SKUModel.objects.get(pk=sku_uid)
        if action == "link":
            contact.skus.add(sku)
            return ModifySKUContactRelationMutation(ok=True)
        elif action == "unlink":
            contact.skus.remove(sku)
            sku.contacts.remove(contact)
            return ModifySKUContactRelationMutation(ok=True)
        return ModifySKUContactRelationMutation(ok=False)


class SKUInput(graphene.InputObjectType):
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
    class Arguments:
        data = SKUInput(required=True)
        uid = graphene.ID()

    sku = graphene.Field(SKU)

    @classmethod
    def mutate(cls, root, info, data, uid=None):
        sku_kwargs = {k: v for k, v in data.items() if v is not None}
        try:
            SKUModel.objects.filter(pk=uid).update(**sku_kwargs)
            sku = SKUModel.objects.get(pk=uid)
        except SKUModel.DoesNotExist:
            sku = SKUModel.objects.create(**sku_kwargs)
        return ModifySKUMutation(sku=sku)


class BeginInvoiceMutation(graphene.Mutation):
    class Arguments:
        job_uid = graphene.String()
        due_date = graphene.DateTime()
        metadata = generic.GenericScalar()

    invoice = graphene.Field(Invoice)

    @classmethod
    def mutate(cls, root, info, job_uid=None, due_date=None, metadata=None):
        metadata = metadata or {}
        invoice = InvoiceModel.objects.create(
            due_date=due_date, metadate=metadata, job_uid=job_uid
        )
        return BeginInvoiceMutation(invoice=invoice)


class SetInvoiceStateMutation(graphene.Mutation):
    class Arguments:
        uid = graphene.ID(required=True)
        state = graphene.Int(required=True)

    invoice = graphene.Field(Invoice)

    @classmethod
    def mutate(cls, root, info, uid, state):
        invoice = Invoice.models.get(pk=uid)
        invoice.state = state
        invoice.save()
        return SetInvoiceStateMutation(invoice=invoice)


class SetInvoiceMetadataMutation(graphene.Mutation):
    class Arguments:
        uid = graphene.ID(required=True)
        metadata = generic.GenericScalar(required=True)

    invoice = graphene.Field(Invoice)

    @classmethod
    def mutate(cls, root, info, uid, metadata):
        invoice = Invoice.models.get(pk=uid)
        invoice.metadata = metadata
        invoice.save()
        return SetInvoiceMetadataMutation(invoice=invoice)


class AddLineItemMutation(graphene.Mutation):
    class Arguments:
        invoice_uid = graphene.ID(required=True)
        sku_uid = graphene.String(required=True)
        price = graphene.Float()
        quantity = graphene.Float()

    line_item = graphene.Field(LineItem)

    @classmethod
    def mutate(cls, root, info, invoice_uid, sku_uid, price=None, quantity=None):
        li_kwargs = {}
        if price:
            li_kwargs["price"] = price
        if quantity:
            li_kwargs["quantity"] = quantity
        invoice = InvoiceModel.objects.get(pk=invoice_uid)
        sku = SKU.objects.get(pk=sku_uid)
        sku.add_to_invoice(invoice, **li_kwargs)
        invoice.update_balances()
        return AddLineItemMutation(invoice=invoice)


class DeleteLineItemMutation(graphene.Mutation):
    class Arguments:
        uid = graphene.ID(required=True)

    invoice = graphene.Field(Invoice)

    @classmethod
    def mutate(cls, root, info, uid):
        li = LineItemModel.objects.get(pk=uid)
        invoice_uid = li.invoice.uid
        invoice = InvoiceModel.objects.get(pk=invoice_uid)
        li.delete()
        invoice.update_balances()
        return DeleteLineItemMutation(invoice=invoice)


class ApplyCreditMutation(graphene.Mutation):
    class Arguments:
        invoice_uid = graphene.ID(required=True)
        amount = graphene.Float(required=True)
        memo = graphene.String()
        metadata = generic.GenericScalar()

    credit = graphene.Field(Credit)

    @classmethod
    def mutate(cls, root, info, invoice_uid, amount, memo="", metadata=None):
        invoice = InvoiceModel.objects.get(pk=invoice_uid)
        credit = invoice.credits.create(
            amount=amount, memo=memo, metadata=metadata or {}
        )
        return ApplyCreditMutation(credit=credit)


class DeleteCreditMutation(graphene.Mutation):
    class Arguments:
        credit_uid = graphene.ID(required=True)

    invoice = graphene.Field(Invoice)

    @classmethod
    def mutate(cls, root, info, credit_uid):
        credit = CreditModel.objects.get(pk=credit_uid)
        invoice_uid = credit.invoice.uid
        credit.delete()
        invoice = InvoiceModel.objects.get(pk=invoice_uid)
        return DeleteCreditMutation(invoice=invoice)


class GenerateInvoicePreviewMutation(graphene.Mutation):
    class Arguments:
        uid = graphene.ID()

    url = graphene.String()

    @classmethod
    def mutate(cls, root, info, uid):
        # do some rendering junk, upload it, and return a link
        invoice = InvoiceModel.objects.get(pk=uid)
        return GenerateInvoicePreviewMutation(url=f"/INVOICE-{invoice.uid}.pdf")


METADATA_MODELS = (
    ClientModel,
    ContactModel,
    VesselModel,
    JobModel,
    TaskModel,
    SKUModel,
    InvoiceModel,
    LineItemModel,
)


class ModifyMetadataMutation(graphene.Mutation):
    class Arguments:
        uid = graphene.ID(required=True)
        metadata = generic.GenericScalar(required=True)
        mode = graphene.String()

    metadata = generic.GenericScalar()
    uid = graphene.UUID()
    parent_type = graphene.String()
    mode = graphene.String()

    @classmethod
    def mutate(cls, root, info, uid, metadata, mode="update"):
        for m in METADATA_MODELS:
            try:
                o = m.objects.get(pk=uid)
                break
            except m.DoesNotExist:
                pass
        else:
            raise Exception(f"Object with UUID {uid} not found")
        initial = o.metadata
        if mode == "update":
            initial.update(metadata)
            o.metadata = initial
        elif mode == "replace":
            o.metadata = metadata
        o.save()
        final = o.metadata
        return ModifyMetadataMutation(
            uid=uid, metadata=final, parent_type=o.__class__.__name__, mode=mode
        )


class Mutations(graphene.ObjectType):
    modify_contact = ModifyContactMutation.Field()
    modify_contact_connection = ModifyClientConnectionMutation.Field()
    modify_sku_relation = ModifySKURelationMutation.Field()
    modify_sku_contact_relation = ModifySKUContactRelationMutation.Field()
    modify_client = ModifyClientMutation.Field()
    modify_vessel = ModifyVesselMutation.Field()
    modify_job = ModifyJobMutation.Field()
    modify_sku = ModifySKUMutation.Field()
    modify_metadata = ModifyMetadataMutation.Field()

    begin_invoice = BeginInvoiceMutation.Field()
    set_invoice_state = SetInvoiceStateMutation.Field()
    set_invoice_metadata = SetInvoiceMetadataMutation.Field()
    get_invoice_pdf_preview = GenerateInvoicePreviewMutation.Field()

    add_line_item = AddLineItemMutation.Field()
    delete_line_item = DeleteLineItemMutation.Field()

    apply_credit = ApplyCreditMutation.Field()
    delete_credit = DeleteCreditMutation.Field()


class InvoiceFilterSet(django_filters.FilterSet):
    class Meta:
        model = InvoiceModel
        exclude = ["metadata"]


class InvoiceNode(DjangoObjectType):
    class Meta:
        model = InvoiceModel
        interfaces = (relay.Node,)
        filterset_class = InvoiceFilterSet

    uid = graphene.UUID(source="pk")
    metadata = generic.GenericScalar()


class SKUFilterSet(django_filters.FilterSet):
    class Meta:
        model = SKUModel
        fields = {
            "uid": ["exact"],
            "default_price": ["exact", "lte", "gte", "lt", "gt"]
        }

    tag = django_filters.CharFilter(method="tag_filter")
    sku_type = django_filters.CharFilter(method="type_filter")
    name = django_filters.CharFilter(method="name_filter")

    def name_filter(self, queryset, name, value):
        return queryset.filter(name__icontains=value)

    def tag_filter(self, queryset, name, value):
        return queryset.filter(metadata__tag=value)

    def type_filter(self, queryset, name, value):
        return queryset.filter(metadata__type=value)


class SKUNode(DjangoObjectType):
    class Meta:
        model = SKUModel
        interfaces = (relay.Node,)
        filterset_class = SKUFilterSet

    uid = graphene.UUID(source="pk")
    metadata = generic.GenericScalar()


class ContactFilterSet(django_filters.FilterSet):
    class Meta:
        model = ContactModel
        exclude = ["metadata"]
        fields = {
            "uid": ["exact"],
            "first_name": ["exact", "icontains"],
            "last_name": ["exact", "icontains"],
            "role": ["exact", "icontains"],
            "billing_address": ["icontains"],
            "mailing_address": ["icontains"],
            "primary_email": ["exact", "icontains"],
        }


class ContactNode(DjangoObjectType):
    class Meta:
        model = ContactModel
        interfaces = (relay.Node,)
        filterset_class = ContactFilterSet

    name = graphene.String(source="name")
    fullname = graphene.String(source="fullname")
    uid = graphene.UUID(source="pk")
    metadata = generic.GenericScalar()

    image_url = graphene.String()
    attachments = graphene.List(Attachment)

    def resolve_image_url(self, info):
        if not self.image:
            return ""
        return self.image.url

    def resolve_attachments(self, info):
        return self.attachments.all()


class ClientNode(DjangoObjectType):
    class Meta:
        model = ClientModel
        interfaces = (relay.Node,)
        filter_fields = {"uid": ["exact"], "company": ["exact", "icontains"]}

    uid = graphene.UUID(source="pk")
    metadata = generic.GenericScalar()


class AttachmentNode(DjangoObjectType):
    class Meta:
        model = AttachmentModel
        interfaces = (relay.Node,)
        filter_fields = {
            "uid": ["exact"]
        }

    metadata = generic.GenericScalar()
    url = graphene.String()
    attached_to = graphene.String()

    def resolve_url(self, info):
        return self.attached_file.url

    def resolve_attached_to(self, info):
        return self.content_object.__class__.__name__


class Query(graphene.ObjectType):
    invoices = DjangoFilterConnectionField(InvoiceNode)
    skus = DjangoFilterConnectionField(SKUNode)
    clients = DjangoFilterConnectionField(ClientNode)
    contacts = DjangoFilterConnectionField(ContactNode)
    attachments = DjangoFilterConnectionField(AttachmentNode)

    invoice = graphene.Field(Invoice, uid=graphene.ID(required=True))
    sku = graphene.Field(SKU, uid=graphene.ID(required=True))
    service_sku = graphene.Field(ServiceSKU, uid=graphene.ID(required=True))
    client = graphene.Field(Client, uid=graphene.ID(required=True))
    contact = graphene.Field(Contact, uid=graphene.ID(required=True))

    def resolve_invoice(root, info, uid):
        return InvoiceModel.objects.get(pk=uid)

    def resolve_sku(root, info, uid):
        return SKUModel.objects.get(pk=uid)

    def resolve_service_sku(root, info, uid):
        return ServiceSKUModel.objects.get(pk=uid)

    def resolve_client(root, info, uid):
        return ClientModel.objects.get(pk=uid)

    def resolve_contact(root, info, uid):
        return ContactModel.objects.get(pk=uid)


schema = graphene.Schema(query=Query, mutation=Mutations)
