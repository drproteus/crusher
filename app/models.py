from django.db import models, transaction
from decimal import Decimal
from django.conf import settings


class Client(models.Model):
    company = models.CharField(max_length=256)
    email = models.EmailField(max_length=256, blank=True)
    mobile = models.CharField(max_length=256, blank=True)
    mailing_address = models.TextField(blank=True)
    billing_address = models.TextField(blank=True)
    metadata = models.JSONField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Vessel(models.Model):
    name = models.CharField(max_length=256)
    mmsi = models.CharField(max_length=9, help_text="Maritime Mobile Service Identity")
    client = models.ForeignKey(Client, on_delete=models.CASCADE, null=False)
    metadata = models.JSONField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Request(models.Model):
    class RequestState(models.IntegerChoices):
        RECEIVED = 0
        IN_PROGRESS = 1
        REJECTED = -1
        PROCESSED = 2

    state = models.IntegerField(
        choices=RequestState.choices, default=RequestState.RECEIVED
    )
    client = models.ForeignKey(Client, on_delete=models.CASCADE, null=False)
    metadata = models.JSONField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Job(models.Model):
    vessel = models.ForeignKey(Vessel, on_delete=models.SET_NULL, null=True)
    origin_request = models.ForeignKey(Request, on_delete=models.SET_NULL, null=True)
    metadata = models.JSONField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


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

    def create(self, staff_data, **sku_kwargs):
        sku_kwargs["metadata"] = sku_kwargs.get("metadata", {"type": "staff"})
        sku_kwargs["metadata"].update(staff_data)
        sku_kwargs["units"] = sku_kwargs.get("units", "hour")
        # VALIDATE
        return super().create(**sku_kwargs)


class ItemManager(SKUManager):
    def get_queryset(self):
        return super().get_queryset().filter(metadata__type="item")

    def create(self, item_data, **sku_kwargs):
        sku_kwargs["metadata"] = sku_kwargs.get("metadata", {"type": "item"})
        sku_kwargs["metadata"].update(item_data)
        # VALIDATE
        return super().create(**sku_kwargs)


class TransportationManager(SKUManager):
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
    objects = SKUManager()

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

    job = models.ForeignKey(Job, on_delete=models.SET_NULL, null=True)
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
        self.initial_balance, self.paid_balance = (
            self.get_initial_balance(),
            self.get_paid_balance(),
        )
        self.save()


class LineItem(models.Model):
    invoice = models.ForeignKey(
        Invoice, on_delete=models.CASCADE, related_name="line_items"
    )
    sku = models.ForeignKey(SKU, null=True, on_delete=models.SET_NULL)
    quantity = models.DecimalField(max_digits=32, decimal_places=2)
    price = models.DecimalField(max_digits=32, decimal_places=2)
    subtotal = models.DecimalField(max_digits=32, decimal_places=2)
    posted_date = models.DateTimeField(auto_now_add=True)
    service_date = models.DateTimeField(auto_now_add=True)
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


from django.contrib import admin


@admin.register(Client, Vessel, Request, Job, SKU, LineItem, Invoice, Credit)
class CrusherAdmin(admin.ModelAdmin):
    pass
