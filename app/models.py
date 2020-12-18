from django.db import models, transaction
from decimal import Decimal
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from app.metadata import (
    StaffMetadataSchema,
    ItemMetadataSchema,
    TransportMetadataSchema,
)
import uuid


class Client(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.CharField(max_length=256)
    email = models.EmailField(max_length=256, blank=True, default="")
    mobile = models.CharField(max_length=256, blank=True, default="")
    mailing_address = models.TextField(blank=True, default="")
    billing_address = models.TextField(blank=True, default="")
    metadata = models.JSONField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company}[{self.id}]"


class Vessel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=256)
    mmsi = models.CharField(max_length=9, blank=True, default="", help_text="Maritime Mobile Service Identity")
    client = models.ForeignKey(
        Client, on_delete=models.CASCADE, null=False, related_name="vessels"
    )
    metadata = models.JSONField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name}[{self.id}]"


class Request(models.Model):
    class RequestState(models.IntegerChoices):
        RECEIVED = 0
        IN_PROGRESS = 1
        REJECTED = -1
        PROCESSED = 2

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    state = models.IntegerField(
        choices=RequestState.choices, default=RequestState.RECEIVED
    )
    client = models.ForeignKey(
        Client, on_delete=models.CASCADE, null=False, related_name="requests"
    )
    metadata = models.JSONField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.state}|{self.client}|{self.created_at}|{self.id}"


class Job(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vessel = models.ForeignKey(
        Vessel, on_delete=models.SET_NULL, null=True, related_name="jobs"
    )
    origin_request = models.ForeignKey(Request, on_delete=models.SET_NULL, null=True)
    metadata = models.JSONField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.vessel.name}|{self.created_at}|{self.id}"


class SKUQuerySet(models.QuerySet):
    def add_to_invoice(self, invoice):
        new_line_item_ids = set()
        with transaction.atomic():
            for sku in self.all():
                li = sku.add_to_invoice(invoice)
                new_line_item_ids.add(li.id)
        return LineItem.objects.filter(id__in=new_line_item_ids)


class SKUManager(models.Manager):
    def get_queryset(self):
        return SKUQuerySet(self.model, using=self._db)


class StaffManager(SKUManager):
    def get_queryset(self):
        return super().get_queryset().filter(metadata__type="staff")

    def create(self, staff_data=None, **sku_kwargs):
        sku_kwargs["units"] = sku_kwargs.get("units", "hour")
        sku_kwargs["metadata"] = StaffMetadataSchema().load(staff_data or {})
        return super().create(**sku_kwargs)


class ItemManager(SKUManager):
    def get_queryset(self):
        return super().get_queryset().filter(metadata__type="item")

    def create(self, item_data=None, **sku_kwargs):
        sku_kwargs["metadata"] = ItemMetadataSchema().load(item_data or {})
        return super().create(**sku_kwargs)


class TransportationManager(SKUManager):
    def get_queryset(self):
        return super().get_queryset().filter(metadata__type="transport")

    def create(self, transport_data=None, **sku_kwargs):
        sku_kwargs["units"] = sku_kwargs.get("units", "mile")
        sku_kwargs["metadata"] = TransportMetadataSchema().load(transport_data or {})
        return super().create(**sku_kwargs)


class SKU(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(blank=True, max_length=256)
    metadata = models.JSONField()
    default_quantity = models.DecimalField(
        default=Decimal(1.0), max_digits=32, decimal_places=2
    )
    default_price = models.DecimalField(
        default=Decimal(1.0), max_digits=32, decimal_places=2
    )
    minimum_quantity = models.DecimalField(null=True, max_digits=32, decimal_places=2)
    minimum_price = models.DecimalField(null=True, max_digits=32, decimal_places=2)
    maximum_quantity = models.DecimalField(null=True, max_digits=32, decimal_places=2)
    maximum_price = models.DecimalField(null=True, max_digits=32, decimal_places=2)
    units = models.CharField(blank=True, max_length=32, default="unit")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    staff = StaffManager()
    items = ItemManager()
    transportation = TransportationManager()
    objects = SKUManager()

    def add_to_invoice(self, invoice, **li_kwargs):
        li_kwargs = li_kwargs or {}
        li_kwargs["quantity"] = li_kwargs.get("quantity", self.default_quantity)
        li_kwargs["price"] = li_kwargs.get("price", self.default_price)
        return LineItem.objects.create(sku=self, invoice=invoice, **li_kwargs)

    @property
    def sku_type(self):
        if self.metadata and self.metadata.get("type"):
            return self.metadata["type"]
        return "misc"

    def __str__(self):
        return f"{self.name}|{self.created_at}|{self.sku_type}|{self.id}"


class Invoice(models.Model):
    class InvoiceState(models.IntegerChoices):
        DRAFT = 0
        OPEN = 1
        PAID_PARTIAL = 2
        PAID_FULL = 3
        CLOSED = 4
        VOID = -1

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey(
        Client, on_delete=models.SET_NULL, null=True, related_name="invoices"
    )
    job = models.ForeignKey(
        Job, on_delete=models.SET_NULL, null=True, related_name="invoices"
    )
    state = models.IntegerField(
        choices=InvoiceState.choices, default=InvoiceState.DRAFT
    )
    initial_balance = models.DecimalField(max_digits=32, decimal_places=2, default=0)
    paid_balance = models.DecimalField(max_digits=32, decimal_places=2, default=0)
    due_date = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    metadata = models.JSONField(null=True)

    def __str__(self):
        return f"{self.state}|{self.created_at}|INITIAL:{self.initial_balance}|PAID:{self.paid_balance}|DUE:{self.due_date}|{self.id}"

    def get_initial_balance(self):
        return sum(self.line_items.all().values_list("subtotal", flat=True))

    def get_paid_balance(self):
        return sum(self.credits.all().values_list("amount", flat=True))

    def get_remaining_balance(self):
        return self.get_initial_balance() - self.get_paid_balance()

    @property
    def remaining_balance(self):
        return self.initial_balance - self.paid_balance

    def update_balances(self):
        self.initial_balance, self.paid_balance = (
            self.get_initial_balance(),
            self.get_paid_balance(),
        )
        self.save()


class LineItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    invoice = models.ForeignKey(
        Invoice, on_delete=models.CASCADE, related_name="line_items"
    )
    sku = models.ForeignKey(SKU, null=True, on_delete=models.SET_NULL, related_name="+")
    quantity = models.DecimalField(max_digits=32, decimal_places=2)
    price = models.DecimalField(max_digits=32, decimal_places=2)
    subtotal = models.DecimalField(max_digits=32, decimal_places=2)
    posted_date = models.DateTimeField(auto_now_add=True)
    service_date = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"INV_ID:{self.invoice.id}|{self.created_at}|SUBTOTAL:{self.subtotal}|POSTED:{self.posted_date}|SERVICE:{self.service_date}|{self.id}"

    def save(self, *args, **kwargs):
        self.subtotal = self.price * self.quantity
        return super().save()


class Credit(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    invoice = models.ForeignKey(
        Invoice, on_delete=models.CASCADE, related_name="credits"
    )
    amount = models.DecimalField(max_digits=32, decimal_places=2)
    memo = models.TextField(blank=True)
    line_item = models.ForeignKey(
        LineItem, on_delete=models.SET_NULL, null=True, related_name="applied_credits"
    )
    posted_date = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"INV_ID:{self.invoice.id}|{self.created_at}|AMOUNT:{self.subtotal}|POSTED:{self.posted_date}|{self.id}"
