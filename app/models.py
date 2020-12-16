from django.db import models
from decimal import Decimal
from enum import Enum


class Client(models.Model):
    name = models.CharField(max_length=256, default="Item")
    email = models.EmailField(max_length=256, blank=True)
    mobile = models.CharField(max_length=256, blank=True)
    mailing_address = models.TextField(blank=True)
    billing_address = models.TextField(blank=True)


class Staff(models.Model):
    first_name = models.CharField(max_length=256, default="Leonard")
    last_name = models.CharField(max_length=256, default="McCoy")
    designation = models.CharField(max_length=256, default="Chief Medical Officer")
    email = models.EmailField(max_length=256, blank=True)
    mobile = models.CharField(max_length=256, blank=True)
    mailing_address = models.TextField(blank=True)
    billing_address = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    def new_sku(self, **sku_kwargs):
        sku = SKU(**sku_kwargs, staff=self)
        sku.save()
        return sku


class Item(models.Model):
    name = models.CharField(max_length=256, default="Item")
    description = models.TextField(blank=True)
    stock = models.DecimalField(max_digits=32, decimal_places=2, default=Decimal(1.00))

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
        return self.filter(item__is_null=True, staff_is_null=True)


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
    default_rate = models.DecimalField(
        default=Decimal(1.0), max_digits=32, decimal_places=2
    )
    units = models.CharField(blank=True, max_length=32, default="unit")

    objects = SKUManager()

    def save(self, *args, **kwargs):
        sku_model = self.staff or self.item
        if sku_model:
            self.name = f"{sku_model.name} @ {self.default_quantity} x {self.default_rate}/{self.units}"
        super().save()


class InvoiceState(Enum):
    DRAFT = 0
    OPEN = 1
    PAID_PARTIAL = 2
    PAID_FULL = 3
    CLOSED = 4
    VOID = -1


class Invoice(models.Model):
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True)
    state = models.IntegerField(
        choices=[(st, st.value) for st in InvoiceState], default=InvoiceState.DRAFT
    )
    initial_balance = models.DecimalField(max_digits=32, decimal_places=2)
    paid_balance = models.DecimalField(max_digits=32, decimal_places=2)


class LineItem(models.Model):
    invoice = models.ForeignKey(
        Invoice, on_delete=models.CASCADE, related_name="line_items"
    )
    sku = models.ForeignKey(SKU, null=True, on_delete=models.SET_NULL)
    quantity = models.DecimalField(max_digits=32, decimal_places=2)
    rate = models.DecimalField(max_digits=32, decimal_places=2)
    subtotal = models.DecimalField(max_digits=32, decimal_places=2)

    def save(self, *args, **kwargs):
        self.subtotal = self.rate * self.quantity
        return super().save()
