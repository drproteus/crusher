from django.db import models
from decimal import Decimal
from enum import Enum
from mixer.backend.django import mixer


class Client(models.Model):
    company_name = models.CharField(max_length=256)
    email = models.EmailField(max_length=256, blank=True)
    mobile = models.CharField(max_length=256, blank=True)
    mailing_address = models.TextField(blank=True)
    billing_address = models.TextField(blank=True)


class Staff(models.Model):
    first_name = models.CharField(max_length=256)
    last_name = models.CharField(max_length=256)
    role = models.CharField(max_length=256)
    email = models.EmailField(max_length=256, blank=True)
    phone_number = models.CharField(max_length=256, blank=True)
    mailing_address = models.TextField(blank=True)
    billing_address = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    def new_sku(self, **sku_kwargs):
        sku = SKU(**sku_kwargs, staff=self)
        sku.save()
        return sku


class Item(models.Model):
    name = models.CharField(max_length=256)
    description = models.TextField(blank=True)
    stock = models.DecimalField(max_digits=32, decimal_places=2, default=Decimal(1.00))
    upc = models.CharField(max_length=256, blank=True)

    def new_sku(self, **sku_kwargs):
        sku = SKU(**sku_kwargs, item=self)
        sku.save()
        return sku


class SKUQuerySet(models.QuerySet):
    def staff(self):
        return self.filter(staff__is_null=False, item__is_null=True)

    def items(self):
        return self.filter(item__is_null=False, staff__is_null=True)

    def other(self):
        return self.filter(item__is_null=True, staff__is_null=True)


class SKUManager(models.Manager):
    def get_queryset(self):
        return SKUQuerySet(self.model, using=self._db)

    def staff(self):
        return self.get_queryset().staff()

    def items(self):
        return self.get_queryset().items()


class SKU(models.Model):
    name = models.CharField(blank=True, max_length=256)
    staff = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True)
    item = models.ForeignKey(Item, on_delete=models.SET_NULL, null=True)
    default_quantity = models.DecimalField(
        default=Decimal(1.0), max_digits=32, decimal_places=2
    )
    default_price = models.DecimalField(
        default=Decimal(1.0), max_digits=32, decimal_places=2
    )
    units = models.CharField(blank=True, max_length=32, default="unit")

    objects = SKUManager()

    def add_to_invoice(self, invoice, **li_kwargs):
        li_kwargs = li_kwargs or {}
        li_kwargs["quantity"] = li_kwargs.get("quantity", self.default_quantity)
        li_kwargs["price"] = li_kwargs.get("price", self.default_price)
        li = LineItem(sku=self, invoice=invoice, **li_kwargs)
        li.save()
        return li


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


class LineItem(models.Model):
    invoice = models.ForeignKey(
        Invoice, on_delete=models.CASCADE, related_name="line_items"
    )
    sku = models.ForeignKey(SKU, null=True, on_delete=models.SET_NULL)
    quantity = models.DecimalField(max_digits=32, decimal_places=2)
    price = models.DecimalField(max_digits=32, decimal_places=2)
    subtotal = models.DecimalField(max_digits=32, decimal_places=2)

    def save(self, *args, **kwargs):
        self.subtotal = self.price * self.quantity
        return super().save()


mixer.register(
    Staff,
    role=lambda: mixer.faker.job(),
    phone_number=lambda: mixer.faker.phone_number(),
    mailing_address=lambda: mixer.faker.address(),
    billing_address=lambda: mixer.faker.address(),
)
mixer.register(Item, upc=lambda: mixer.faker.ean())
mixer.register(Invoice)
