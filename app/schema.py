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
    FormTemplate as FormTemplateModel,
    RenderedForm as RenderedFormModel,
)

from app.nodes import *


class ModifyFormTemplateMutation(graphene.Mutation):
    class Arguments:
        uid = graphene.UUID()
        name = graphene.String(required=False)
        fields = generic.GenericScalar()
        update_fields = graphene.Boolean()

    form_template = graphene.Field(FormTemplateNode)

    @classmethod
    def mutate(cls, root, info, uid, name=None, fields=None, update_fields=False):
        template = FormTemplateModel.objects.get(pk=uid)
        if name:
            template.name = name
        if fields:
            original = template.fields
            if update_fields:
                original.update(fields)
                template.fields = original
            else:
                template.fields = fields
        return ModifyFormTemplateMutation(form_template=template)


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
        uid = graphene.UUID()

    contact = graphene.Field(ContactNode)

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
        c1_uid = graphene.UUID(required=True)
        c2_uid = graphene.UUID(required=True)
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
    contact_uid = graphene.UUID()
    metadata = generic.GenericScalar()


class DeleteClientContact(graphene.Mutation):
    class Arguments:
        uid = graphene.UUID(required=True)

    client = graphene.Field(ClientNode)

    @classmethod
    def mutate(cls, root, info, uid):
        client = ClientModel.objects.get(pk=uid)
        client.contact_uid = None
        client.save()
        return DeleteClientContact(client=client)


class DeleteClientMutation(graphene.Mutation):
    class Arguments:
        uid = graphene.UUID()

    ok = graphene.Boolean()

    @classmethod
    def mutate(cls, root, info, uid):
        client = ClientModel.objects.get(pk=uid)
        client.delete()
        return DeleteClientMutation(ok=True)


class ModifyClientMutation(graphene.Mutation):
    class Arguments:
        data = ClientInput(required=True)
        uid = graphene.UUID()

    client = graphene.Field(ClientNode)

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
        uid = graphene.UUID()

    vessel = graphene.Field(VesselNode)

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
    vessel_uid = graphene.UUID()
    origin_task_uid = graphene.UUID()
    metadata = generic.GenericScalar()


class ModifyJobMutation(graphene.Mutation):
    class Arguments:
        data = JobInput(required=True)
        uid = graphene.UUID()

    job = graphene.Field(JobNode)

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
        uid = graphene.UUID()

    sku = graphene.Field(SKUNode)

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

    invoice = graphene.Field(InvoiceNode)

    @classmethod
    def mutate(cls, root, info, job_uid=None, due_date=None, metadata=None):
        metadata = metadata or {}
        try:
            job = JobModel.objects.get(pk=job_uid)
            job.invoices.create(due_date=due_date, metadata=metadata)
        except JobModel.DoesNotExist:
            invoice = InvoiceModel.objects.create(due_date=due_date, metadata=metadata)
        return BeginInvoiceMutation(invoice=invoice)


class SetInvoiceStateMutation(graphene.Mutation):
    class Arguments:
        uid = graphene.UUID(required=True)
        state = graphene.Int(required=True)

    invoice = graphene.Field(InvoiceNode)

    @classmethod
    def mutate(cls, root, info, uid, state):
        invoice = Invoice.models.get(pk=uid)
        invoice.state = state
        invoice.save()
        return SetInvoiceStateMutation(invoice=invoice)


class SetInvoiceMetadataMutation(graphene.Mutation):
    class Arguments:
        uid = graphene.UUID(required=True)
        metadata = generic.GenericScalar(required=True)

    invoice = graphene.Field(InvoiceNode)

    @classmethod
    def mutate(cls, root, info, uid, metadata):
        invoice = Invoice.models.get(pk=uid)
        invoice.metadata = metadata
        invoice.save()
        return SetInvoiceMetadataMutation(invoice=invoice)


class AddLineItemMutation(graphene.Mutation):
    class Arguments:
        invoice_uid = graphene.UUID(required=True)
        sku_uid = graphene.String(required=True)
        price = graphene.Float()
        quantity = graphene.Float()

    line_item = graphene.Field(LineItemNode)

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
        uid = graphene.UUID(required=True)

    invoice = graphene.Field(InvoiceNode)

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
        invoice_uid = graphene.UUID(required=True)
        amount = graphene.Float(required=True)
        memo = graphene.String()
        metadata = generic.GenericScalar()

    credit = graphene.Field(CreditNode)

    @classmethod
    def mutate(cls, root, info, invoice_uid, amount, memo="", metadata=None):
        invoice = InvoiceModel.objects.get(pk=invoice_uid)
        credit = invoice.credits.create(
            amount=amount, memo=memo, metadata=metadata or {}
        )
        return ApplyCreditMutation(credit=credit)


class DeleteCreditMutation(graphene.Mutation):
    class Arguments:
        credit_uid = graphene.UUID(required=True)

    invoice = graphene.Field(InvoiceNode)

    @classmethod
    def mutate(cls, root, info, credit_uid):
        credit = CreditModel.objects.get(pk=credit_uid)
        invoice_uid = credit.invoice.uid
        credit.delete()
        invoice = InvoiceModel.objects.get(pk=invoice_uid)
        return DeleteCreditMutation(invoice=invoice)


class GenerateInvoicePreviewMutation(graphene.Mutation):
    class Arguments:
        uid = graphene.UUID()

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
        uid = graphene.UUID(required=True)
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
    delete_client = DeleteClientMutation.Field()
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

    modify_form_template = ModifyFormTemplateMutation.Field()


class Query(graphene.ObjectType):
    invoices = DjangoFilterConnectionField(InvoiceNode)
    skus = DjangoFilterConnectionField(SKUNode)
    clients = DjangoFilterConnectionField(ClientNode)
    contacts = DjangoFilterConnectionField(ContactNode)
    attachments = DjangoFilterConnectionField(AttachmentNode)
    form_templates = DjangoFilterConnectionField(FormTemplateNode)
    rendered_forms = DjangoFilterConnectionField(RenderedFormNode)

    invoice = graphene.Field(InvoiceNode, uid=graphene.UUID(required=True))
    sku = graphene.Field(SKUNode, uid=graphene.UUID(required=True))
    client = graphene.Field(ClientNode, uid=graphene.UUID(required=True))
    contact = graphene.Field(ContactNode, uid=graphene.UUID(required=True))
    attachment = graphene.Field(AttachmentNode, uid=graphene.UUID(required=True))

    def resolve_invoice(root, info, uid):
        return InvoiceModel.objects.get(pk=uid)

    def resolve_sku(root, info, uid):
        return SKUModel.objects.get(pk=uid)

    def resolve_client(root, info, uid):
        return ClientModel.objects.get(pk=uid)

    def resolve_contact(root, info, uid):
        return ContactModel.objects.get(pk=uid)

    def resolve_attachment(root, info, uid):
        return AttachmentModel.objects.get(pk=uid)


schema = graphene.Schema(query=Query, mutation=Mutations)
