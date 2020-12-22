import django_filters
import graphene
from graphene import relay
from graphene.types import generic
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from app.metadata import (
    ItemMetadataSchema,
    ServiceMetadataSchema,
    SKUMetadataSchema,
    TransportMetadataSchema,
    TransportPointSchema,
    VoyagePointSchema,
)
from app.models import SKU as SKUModel
from app.models import Attachment as AttachmentModel
from app.models import Client as ClientModel
from app.models import Contact as ContactModel
from app.models import Credit as CreditModel
from app.models import Invoice as InvoiceModel
from app.models import ItemSKU as ItemSKUModel
from app.models import Job as JobModel
from app.models import LineItem as LineItemModel
from app.models import ServiceSKU as ServiceSKUModel
from app.models import Task as TaskModel
from app.models import TransportationSKU as TransportationSKUModel
from app.models import Vessel as VesselModel
from app.models import FormTemplate as FormTemplateModel
from app.models import RenderedForm as RenderedFormModel


class AttachmentFilterSet(django_filters.FilterSet):
    class Meta:
        model = AttachmentModel
        fields = {"uid": ["exact"]}

    filename = django_filters.CharFilter(method="filename_exact_filter")
    filename_like = django_filters.CharFilter(method="filename_like_filter")
    extension = django_filters.CharFilter(method="filename_extension_filter")

    def name_filter(self, queryset, name, value):
        return queryset.filter(name__icontains=value)

    def filename_exact_filter(self, queryset, name, value):
        return queryset.filter(attached_file=value)

    def filename_like_filter(self, queryset, name, value):
        return queryset.filter(attached_file__icontains=value)

    def filename_extension_filter(self, queryset, name, value):
        return queryset.filter(attached_file__endswith=f".{value}")


class AttachmentNode(DjangoObjectType):
    class Meta:
        model = AttachmentModel
        interfaces = (relay.Node,)
        filterset_class = AttachmentFilterSet

    metadata = generic.GenericScalar()
    url = graphene.String()
    attached_to = graphene.String()

    def resolve_url(self, info):
        return self.attached_file.url

    def resolve_attached_to(self, info):
        return self.content_object.__class__.__name__


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
    attachments = DjangoFilterConnectionField(AttachmentNode)


class SKUFilterSet(django_filters.FilterSet):
    class Meta:
        model = SKUModel
        fields = {
            "uid": ["exact"],
            "default_price": ["exact", "lte", "gte", "lt", "gt"],
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
    attachments = DjangoFilterConnectionField(AttachmentNode)
    image_url = graphene.String()

    def resolve_image_url(self, info):
        if self.image:
            return self.image.url
        return ""


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
    attachments = DjangoFilterConnectionField(AttachmentNode)
    image_url = graphene.String()

    def resolve_image_url(self, info):
        if self.image:
            return self.image.url
        return ""

    def resolve_attachments(self, info):
        return self.attachments.all()


class ClientNode(DjangoObjectType):
    class Meta:
        model = ClientModel
        interfaces = (relay.Node,)
        filter_fields = {"uid": ["exact"], "company": ["exact", "icontains"]}

    uid = graphene.UUID(source="pk")
    metadata = generic.GenericScalar()
    attachments = DjangoFilterConnectionField(AttachmentNode)
    image_url = graphene.String()
    invoice_counts = generic.GenericScalar()

    def resolve_image_url(self, info):
        if self.image:
            return self.image.url
        return ""

    def resolve_invoice_counts(self, info):
        return {
            "open": self.invoices.filter(state=1).count(),
            "paid_partial": self.invoices.filter(state=2).count(),
            "paid_full": self.invoices.filter(state=3).count(),
            "drafts": self.invoices.filter(state=0).count(),
            "closed": self.invoices.filter(state=4).count(),
            "void": self.invoices.filter(state=-1).count(),
        }


class VesselNode(DjangoObjectType):
    class Meta:
        model = VesselModel
        interfaces = (relay.Node,)
        filter_fields = {"uid": ["exact"], "name": ["exact", "icontains"]}

    metadata = generic.GenericScalar()
    attachments = DjangoFilterConnectionField(AttachmentNode)
    image_url = graphene.String()

    def resolve_image_url(self, info):
        if self.image:
            return self.image.url
        return ""


class TaskNode(DjangoObjectType):
    class Meta:
        model = TaskModel
        interfaces = (relay.Node,)
        filter_fields = {"uid": ["exact"]}

    metadata = generic.GenericScalar()
    attachments = DjangoFilterConnectionField(AttachmentNode)


class JobNode(DjangoObjectType):
    class Meta:
        model = JobModel
        interfaces = (relay.Node,)
        filter_fields = {"uid": ["exact"]}

    metadata = generic.GenericScalar()
    attachments = DjangoFilterConnectionField(AttachmentNode)


class LineItemNode(DjangoObjectType):
    class Meta:
        model = LineItemModel
        interfaces = (relay.Node,)
        filter_fields = {
            "uid": ["exact"],
            "invoice": ["exact"],
            "subtotal": ["exact", "lt", "lte", "gt", "gte"],
        }

    metadata = generic.GenericScalar()


class CreditNode(DjangoObjectType):
    class Meta:
        model = CreditModel
        interfaces = (relay.Node,)
        filter_fields = {
            "uid": ["exact"],
            "invoice": ["exact"],
            "amount": ["exact", "lt", "lte", "gt", "gte"],
        }


class FormTemplateNode(DjangoObjectType):
    class Meta:
        model = FormTemplateModel
        interfaces = (relay.Node,)
        filter_fields = {"uid": ["exact"], "name": ["exact", "icontains"]}

    fields = generic.GenericScalar()
    metadata = generic.GenericScalar()
    url = graphene.String()
    annotations = generic.GenericScalar()

    def resolve_url(self, info):
        if not self.template_file:
            return ""
        return self.template_file.url


class RenderedFormNode(DjangoObjectType):
    class Meta:
        model = RenderedFormModel
        interfaces = (relay.Node,)
        filter_fields = {"uid": ["exact"]}

    metadata = generic.GenericScalar()
    rendering_data = generic.GenericScalar()
    url = graphene.String()

    def resolve_url(self, info):
        if not self.rendered_file:
            return ""
        return self.rendered_file.url
