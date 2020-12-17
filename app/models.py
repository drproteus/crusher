from django.db import models, transaction
from decimal import Decimal
from enum import Enum
from django.conf import settings


class Client(models.Model):
    company = models.CharField(max_length=256)
    email = models.EmailField(max_length=256, blank=True)
    mobile = models.CharField(max_length=256, blank=True)
    mailing_address = models.TextField(blank=True)
    billing_address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Staff(models.Model):
    title = models.CharField(max_length=32, blank=True)
    first_name = models.CharField(max_length=256)
    last_name = models.CharField(max_length=256)
    role = models.CharField(max_length=256)
    email = models.EmailField(max_length=256, blank=True)
    phone_number = models.CharField(max_length=256, blank=True)
    mailing_address = models.TextField(blank=True)
    billing_address = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def name(self):
        name = f"{self.first_name} {self.last_name}"
        if self.title:
            return f"{self.title} {name}"
        return name

    def new_sku(self, **sku_kwargs):
        sku_kwargs["units"] = sku_kwargs.get("units", "hour")
        sku = SKU(**sku_kwargs, staff=self)
        sku.save()
        return sku


class Item(models.Model):
    name = models.CharField(max_length=256)
    description = models.TextField(blank=True)
    stock = models.DecimalField(max_digits=32, decimal_places=2, default=Decimal(1.00))
    upc = models.CharField(max_length=256, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def new_sku(self, **sku_kwargs):
        sku = SKU(**sku_kwargs, item=self)
        sku.save()
        return sku


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
    minium_quantity = models.DecimalField(
        null=True, max_digits=32, decimal_places=2
    )
    minimum_price = models.DecimalField(
        null=True, max_digits=32, decimal_places=2
    )
    maximum_quantity = models.DecimalField(
        null=True, max_digits=32, decimal_places=2
    )
    maximum_price = models.DecimalField(
        null=True, max_digits=32, decimal_places=2
    )
    units = models.CharField(blank=True, max_length=32, default="unit")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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


if settings.DEBUG:
    from mixer.backend.django import mixer
    mixer.register(
        Staff,
        role=lambda: mixer.faker.job(),
        phone_number=lambda: mixer.faker.phone_number(),
        mailing_address=lambda: mixer.faker.address(),
        billing_address=lambda: mixer.faker.address(),
    )
    mixer.register(Item, upc=lambda: mixer.faker.ean())
    mixer.register(Invoice)
