from django.db import models, transaction
from decimal import Decimal
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from app.metadata import (
    ItemMetadataSchema,
    TransportMetadataSchema,
    ServiceMetadataSchema,
    CreditMetadataSchema,
)
import uuid

### for rendering --> move elsewhere later
import io
import pdfrw
from reportlab.pdfgen import canvas
from django.core.files.base import ContentFile

###


class Attachment(models.Model):
    uid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=256)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField()
    content_object = GenericForeignKey("content_type", "object_id")
    attached_file = models.FileField(null=False)
    metadata = models.JSONField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Contact(models.Model):
    uid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=256, blank=True, null=True)
    last_name = models.CharField(max_length=256)
    title = models.CharField(max_length=32, blank=True, null=True)
    role = models.CharField(max_length=256, blank=True, null=True)
    primary_email = models.CharField(max_length=256, blank=True, null=True)
    phone_number = models.CharField(max_length=256, blank=True, null=True)
    mailing_address = models.TextField(blank=True, null=True)
    billing_address = models.TextField(blank=True, null=True)
    metadata = models.JSONField(null=True)
    connections = models.ManyToManyField("self")
    image = models.FileField(null=True)
    attachments = GenericRelation(Attachment)

    @property
    def name(self):
        return " ".join([_ for _ in [self.first_name, self.last_name] if _])

    @property
    def fullname(self):
        return " ".join([_ for _ in [self.title, self.first_name, self.last_name] if _])

    def __str__(self):
        s = self.fullname
        if self.primary_email:
            s += f" [{self.primary_email}]"
        return s


class Client(models.Model):
    uid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.CharField(max_length=256)
    metadata = models.JSONField(null=True)
    contact = models.ForeignKey(Contact, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    image = models.FileField(null=True)
    attachments = GenericRelation(Attachment)

    def __str__(self):
        return f"{self.company}[{self.uid}]"


class Vessel(models.Model):
    uid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=256)
    mmsi = models.CharField(
        max_length=9,
        blank=True,
        default="",
        help_text="Maritime Mobile Service Identity",
    )
    client = models.ForeignKey(
        Client, on_delete=models.CASCADE, null=False, related_name="vessels"
    )
    metadata = models.JSONField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    image = models.FileField(null=True)
    attachments = GenericRelation(Attachment)

    def __str__(self):
        return f"{self.name}[{self.uid}]"


class Task(models.Model):
    class TaskState(models.IntegerChoices):
        RECEIVED = 0
        IN_PROGRESS = 1
        REJECTED = -1
        PROCESSED = 2

    uid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    state = models.IntegerField(choices=TaskState.choices, default=TaskState.RECEIVED)
    client = models.ForeignKey(
        Client, on_delete=models.CASCADE, null=False, related_name="tasks"
    )
    contact_mentions = models.ManyToManyField(Contact, related_name="task_mentions")
    metadata = models.JSONField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    attachments = GenericRelation(Attachment)


class Job(models.Model):
    uid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vessel = models.ForeignKey(
        Vessel, on_delete=models.SET_NULL, null=True, related_name="jobs"
    )
    origin_task = models.ForeignKey(Task, on_delete=models.SET_NULL, null=True)
    metadata = models.JSONField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    attachments = GenericRelation(Attachment)

    def __str__(self):
        return f"Job {self.id} [{self.vessel.name}]"


class SKUQuerySet(models.QuerySet):
    def add_to_invoice(self, invoice, **li_kwargs):
        new_line_item_ids = set()
        with transaction.atomic():
            for sku in self.all():
                li = sku.add_to_invoice(invoice, **li_kwargs)
                new_line_item_ids.add(li.uid)
        return LineItem.objects.filter(id__in=new_line_item_ids)


class SKUManager(models.Manager):
    def get_queryset(self):
        return SKUQuerySet(self.model, using=self._db)


class ServiceManager(SKUManager):
    def get_queryset(self):
        return super().get_queryset().filter(metadata__type="service")

    def create(self, service_data=None, **sku_kwargs):
        sku_kwargs["units"] = sku_kwargs.get("units", "hour")
        sku_kwargs["metadata"] = ServiceMetadataSchema().load(service_data or {})
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
    uid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
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

    image = models.FileField(null=True)
    attachments = GenericRelation(Attachment)
    contacts = models.ManyToManyField(Contact, related_name="skus")
    related_skus = models.ManyToManyField("self")

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

    def save(self, *args, **kwargs):
        if self.metadata is None:
            self.metadata = {}
        super().save(*args, **kwargs)


class ServiceSKU(SKU):
    class Meta:
        proxy = True

    objects = ServiceManager()

    def save(self, *args, **kwargs):
        self.metadata = ServiceMetadataSchema().load(
            self.metadata or {"type": "service"}
        )
        super().save(*args, **kwargs)


class ItemSKU(SKU):
    class Meta:
        proxy = True

    objects = ItemManager()

    def save(self, *args, **kwargs):
        self.metadata = ItemMetadataSchema().load(self.metadata or {"type": "item"})
        super().save(*args, **kwargs)


class TransportationSKU(SKU):
    class Meta:
        proxy = True

    objects = TransportationManager()

    def save(self, *args, **kwargs):
        self.metadata = ItemMetadataSchema().load(
            self.metadata or {"type": "transport"}
        )
        super().save(*args, **kwargs)


class Invoice(models.Model):
    class InvoiceState(models.IntegerChoices):
        DRAFT = 0
        OPEN = 1
        PAID_PARTIAL = 2
        PAID_FULL = 3
        CLOSED = 4
        VOID = -1

    uid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
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
    attachments = GenericRelation(Attachment)

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
    uid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
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

    def save(self, *args, **kwargs):
        self.subtotal = self.price * self.quantity
        self.invoice.update_balances()
        return super().save(*args, **kwargs)


class Credit(models.Model):
    uid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    contact = models.ForeignKey(
        Contact, on_delete=models.SET_NULL, null=True, related_name="+"
    )
    invoice = models.ForeignKey(
        Invoice, on_delete=models.CASCADE, related_name="credits"
    )
    amount = models.DecimalField(max_digits=32, decimal_places=2)
    memo = models.TextField(blank=True)
    metadata = models.JSONField(null=True)
    posted_date = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.invoice.update_balances()
        self.metadata = CreditMetadataSchema().load(self.metadata)
        return super().save(*args, **kwargs)


class FormTemplate(models.Model):
    """
    expects a fields object like:
        [{
            "first_name": {
                "type": "annotation",
                "annot_idx": 1,
                "disables": [<annotation indices that get disabled if this is true>]
            },
            "last_name": {
                "type": "point",
                "coords": [32, 32]
            }
        }, ... <page 2> ...]
    """

    uid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=256)
    fields = models.JSONField(null=True)
    default_fields = models.JSONField(null=True)
    template_file = models.FileField()
    metadata = models.JSONField(null=True)
    annotations = models.JSONField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    clients = models.ManyToManyField(Client, related_name="forms")

    @classmethod
    def parse_annotations(cls, template_file):
        annots = []
        if not template_file:
            return annots
        template = pdfrw.PdfReader(template_file)
        for page_num, page in enumerate(template.pages):
            page_annots = {}
            for i, annotation in enumerate(page.Annots):
                field_name = cls.make_annotation_key_valid_json_key(
                    annotation["/T"], page_num, i
                )
                page_annots[field_name] = {
                    "initial_value": annotation["/V"] or "",
                    "annot_idx": i,
                    "page": page_num,
                }
            annots.append(page_annots)
        template_file.seek(0)
        return annots

    @classmethod
    def make_annotation_key_valid_json_key(cls, key, page_num=0, i=0):
        if not key:
            return f"unknown_{page_num}_{i}"
        return key.translate(
            key.maketrans({"(": "_", ")": "_", " ": "_", "'": "_", '"': "_"})
        )

    def write_parsed_annotations(self):
        self.annotations = self.parse_annotations(self.template_file)
        self.save()
        return self.annotations

    def render_with_data(self, data):
        default_fields = self.default_fields or {}
        data.update(default_fields)
        template = self.fill_template_with_annotation_fields(data)
        canvas_data = self.get_overlay_canvas(data)
        form = self.merge(canvas_data, template)
        return self.write_form(form, data)

    def fill_template_with_annotation_fields(self, data_pages):
        template = pdfrw.PdfReader(self.template_file)
        for data_page in data_pages:
            for field_name, field in data_page.items():
                idx = field["annot_idx"]
                page = field.get("page", 0)
                try:
                    annot = template.Root.Pages.Kids[page].Annots[idx]
                    if isinstance(value, bool) and value:
                        annot.update(pdfrw.PdfDict(AS=pdfrw.PdfName("Yes")))
                    else:
                        annot.update(pdfrw.PdfDict(V="{}".format(value)))
                    annot.update(pdfrw.PdfDict(AP=""))
                except Exception as e:
                    print(idx, e)
        return template

    def get_overlay_canvas(self, data_pages):
        data = io.BytesIO()
        pdf = canvas.Canvas(data)
        fields = self.fields or {}
        pdf.setFontSize(size=10)
        started_pdf = False
        for data_page in data_pages:
            if started_pdf:
                pdf._startPage()
            else:
               started_pdf = True
            for field_name, field in data_page.items():
                if field["type"] == "text":
                    x, y = field["coords"]
                    font_size = field.get("size", None)
                    pdf.setFontSize(size=font_size)
                    pdf.drawString(x=x, y=y, text=field_data.get(field_name, ""))
                    pdf.setFontSize(size=10)
                elif field["type"] == "select":
                    x, y = field["coords"]
                    radius = field.get("radius", 2)
                    pdf.circle(x, y, radius, fill=1)
        pdf.save()
        data.seek(0)
        return data

    def merge(self, canvas_data, template):
        overlay_pdf = pdfrw.PdfReader(canvas_data)
        for page, data in zip(template.pages, overlay_pdf.pages):
            overlay = pdfrw.PageMerge().add(data)[0]
            pdfrw.PageMerge(page).add(overlay).render()
        form = io.BytesIO()
        pdfrw.PdfWriter().write(form, template)
        form.seek(0)
        return form

    def write_form(self, form_obj, data):
        pdf_uuid = uuid.uuid4()
        form_filename = f"rendered_forms/{self.name}/{pdf_uuid}.pdf"
        form_obj.name = form_filename
        rendered = ContentFile(form_obj.getvalue(), form_obj.name)
        rendered = RenderedForm.objects.create(
            template=self, rendering_data=data, rendered_file=rendered
        )
        return rendered


class RenderedForm(models.Model):
    uid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    template = models.ForeignKey(
        FormTemplate, on_delete=models.SET_NULL, null=True, related_name="+"
    )
    rendering_data = models.JSONField(null=True)
    rendered_file = models.FileField()
    client = models.ForeignKey(
        Client, on_delete=models.SET_NULL, null=True, related_name="rendered_forms"
    )
    metadata = models.JSONField(null=True)
