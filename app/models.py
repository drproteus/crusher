from django.db import models, transaction
from decimal import Decimal
from enum import Enum
from django.conf import settings
from uuid import uuid4


class Client(models.Model):
    company = models.CharField(max_length=256)
    email = models.EmailField(max_length=256, blank=True)
    mobile = models.CharField(max_length=256, blank=True)
    mailing_address = models.TextField(blank=True)
    billing_address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class StaffManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(metadata__type="staff")

    def create(self, staff_data, **sku_kwargs):
        sku_kwargs["metadata"] = sku_kwargs.get("metadata", {"type": "staff"})
        sku_kwargs["metadata"].update(staff_data)
        sku_kwargs["units"] = sku_kwargs.get("units", "hour")
        # VALIDATE
        return super().create(**sku_kwargs)


class ItemManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(metadata__type="item")

    def create(self, item_data, **sku_kwargs):
        sku_kwargs["metadata"] = sku_kwargs.get("metadata", {"type": "item"})
        sku_kwargs["metadata"].update(item_data)
        # VALIDATE
        return super().create(**sku_kwargs)


class TransportationManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(metadata__type="transport")

    def create(self, transport_data, **sku_kwargs):
        sku_kwargs["metadata"] = sku_kwargs.get("metadata", {"type": "transport"})
        sku_kwargs["metadata"].update(transport_data)
        sku_kwargs["units"] = sku_kwargs.get("units", "mile")
        # VALIDATE
        return super().create(**sku_kwargs)


class SKU(models.Model):
    name = models.CharField(blank=True, max_length=256)
    metadata = models.JSONField()
    default_quantity = models.DecimalField(
        default=Decimal(1.0), max_digits=32, decimal_places=2
    )
    default_price = models.DecimalField(
        default=Decimal(1.0), max_digits=32, decimal_places=2
    )
    minium_quantity = models.DecimalField(null=True, max_digits=32, decimal_places=2)
    minimum_price = models.DecimalField(null=True, max_digits=32, decimal_places=2)
    maximum_quantity = models.DecimalField(null=True, max_digits=32, decimal_places=2)
    maximum_price = models.DecimalField(null=True, max_digits=32, decimal_places=2)
    units = models.CharField(blank=True, max_length=32, default="unit")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    staff = StaffManager()
    items = ItemManager()
    transportation = TransportationManager()

    def add_to_invoice(self, invoice, **li_kwargs):
        li_kwargs = li_kwargs or {}
        li_kwargs["quantity"] = li_kwargs.get("quantity", self.default_quantity)
        li_kwargs["price"] = li_kwargs.get("price", self.default_price)
        return LineItem.objects.create(sku=self, invoice=invoice, **li_kwargs)


class Invoice(models.Model):
    class InvoiceState(models.IntegerChoices):
        DRAFT = 0
        OPEN = 1
        PAID_PARTIAL = 2
        PAID_FULL = 3
        CLOSED = 4
        VOID = -1

    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True)
    state = models.IntegerField(
        choices=InvoiceState.choices, default=InvoiceState.DRAFT
    )
    initial_balance = models.DecimalField(max_digits=32, decimal_places=2, default=0)
    paid_balance = models.DecimalField(max_digits=32, decimal_places=2, default=0)
    due_date = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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
        self.initial_balance = self.get_initial_balance()
        self.paid_balance = self.get_paid_balance()


class LineItem(models.Model):
    invoice = models.ForeignKey(
        Invoice, on_delete=models.CASCADE, related_name="line_items"
    )
    sku = models.ForeignKey(SKU, null=True, on_delete=models.SET_NULL)
    quantity = models.DecimalField(max_digits=32, decimal_places=2)
    price = models.DecimalField(max_digits=32, decimal_places=2)
    subtotal = models.DecimalField(max_digits=32, decimal_places=2)
    posted_date = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.subtotal = self.price * self.quantity
        return super().save()


class Credit(models.Model):
    invoice = models.ForeignKey(
        Invoice, on_delete=models.CASCADE, related_name="credits"
    )
    amount = models.DecimalField(max_digits=32, decimal_places=2)
    memo = models.TextField(blank=True)
    line_item = models.ForeignKey(LineItem, on_delete=models.SET_NULL, null=True)
    posted_date = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
