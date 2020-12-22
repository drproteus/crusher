from datetime import datetime
from uuid import uuid4

from django.core.files.storage import default_storage
from django.shortcuts import Http404, HttpResponse, render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from app.models import (
    Attachment,
    Invoice,
    Client,
    Contact,
    SKU,
    FormTemplate,
    RenderedForm,
)


class FilenameConflictException(Exception):
    pass


@method_decorator(csrf_exempt, name="dispatch")
class AttachmentView(View):
    def delete(self, request, attachment_uid, **kwargs):
        try:
            a = Attchment.objects.get(uid=attachment_uid)
        except Attachment.DoesNotExist:
            raise Http404
        a.delete()
        return HttpResponse(status=200)


# DO NOT LEAVE THIS HERE --> FOR TESTING ONLY
@method_decorator(csrf_exempt, name="dispatch")
class InvoiceAttachmentView(View):
    @classmethod
    def check_for_conflicts(cls, name):
        if not default_storage.exists(name):
            return
        raise FilenameConflictException

    def post(self, request, invoice_uid, **kwargs):
        try:
            invoice = Invoice.objects.get(pk=invoice_uid)
        except Invoice.DoesNotExist:
            raise Http404
        file_obj = request.FILES.get("attachment_file")
        name = request.POST.get("filename", file_obj.name)
        file_obj.name = (
            f"attachments/invoice/{invoice_uid}/{datetime.now().isoformat()}/{file_obj.name}",
        )
        metadata = {}
        for k, v in request.POST.items():
            if k != "filename":
                metadata[k] = v

        try:
            self.check_for_conflicts(name)
        except FilenameConflictException:
            return HttpResponse(status=420)

        invoice.attachments.create(name=name, metadata=metadata, attached_file=file_obj)

        return HttpResponse(status=200)


@method_decorator(csrf_exempt, name="dispatch")
class ClientAttachmentView(View):
    @classmethod
    def check_for_conflicts(cls, name):
        if not default_storage.exists(name):
            return
        raise FilenameConflictException

    def post(self, request, client_uid, **kwargs):
        try:
            client = Client.objects.get(pk=client_uid)
        except Client.DoesNotExist:
            raise Http404
        file_obj = request.FILES.get("attachment_file")
        name = request.POST.get("filename", file_obj.name)
        file_obj.name = (
            f"attachments/client/{client_uid}/{datetime.now().isoformat()}/{file_obj.name}",
        )
        metadata = {}
        for k, v in request.POST.items():
            if k != "filename":
                metadata[k] = v

        try:
            self.check_for_conflicts(name)
        except FilenameConflictException:
            return HttpResponse(status=420)

        client.attachments.create(name=name, metadata=metadata, attached_file=file_obj)

        return HttpResponse(status=200)


@method_decorator(csrf_exempt, name="dispatch")
class ContactAttachmentView(View):
    @classmethod
    def check_for_conflicts(cls, name):
        if not default_storage.exists(name):
            return
        raise FilenameConflictException

    def post(self, request, contact_uid, **kwargs):
        try:
            contact = Contact.objects.get(pk=contact_uid)
        except Contact.DoesNotExist:
            raise Http404
        file_obj = request.FILES.get("attachment_file")
        name = request.POST.get("filename", file_obj.name)
        file_obj.name = (
            f"attachments/contact/{contact_uid}/{datetime.now().isoformat()}/{file_obj.name}",
        )
        metadata = {}
        for k, v in request.POST.items():
            if k != "filename":
                metadata[k] = v

        try:
            self.check_for_conflicts(name)
        except FilenameConflictException:
            return HttpResponse(status=420)

        contact.attachments.create(name=name, metadata=metadata, attached_file=file_obj)

        return HttpResponse(status=200)


@method_decorator(csrf_exempt, name="dispatch")
class ContactImageView(View):
    def delete(self, request, contact_uid, **kwargs):
        try:
            contact = Contact.objects.get(pk=contact_uid)
        except Contact.DoesNotExist:
            raise Http404
        contact.image = None
        contact.save()
        return HttpResponse(status=200)

    def post(self, request, contact_uid, **kwargs):
        try:
            contact = Contact.objects.get(pk=contact_uid)
        except Contact.DoesNotExist:
            raise Http404
        file_obj = request.FILES.get("image")
        if not file_obj:
            return HttpResponse(status=420)
        file_obj.name = f"contact-image-{contact_uid}"

        name = request.POST.get("filename", file_obj.name)
        file_obj.name = (
            f"attachments/contact/{contact_uid}/{datetime.now().isoformat()}/{file_obj.name}",
        )
        contact.image = file_obj
        contact.save()

        return HttpResponse(status=200)


@method_decorator(csrf_exempt, name="dispatch")
class ClientImageView(View):
    def delete(self, request, client_uid, **kwargs):
        try:
            client = Client.objects.get(pk=client_uid)
        except Client.DoesNotExist:
            raise Http404
        client.image = None
        client.save()
        return HttpResponse(status=200)

    def post(self, request, client_uid, **kwargs):
        try:
            client = Client.objects.get(pk=client_uid)
        except Client.DoesNotExist:
            raise Http404
        file_obj = request.FILES.get("image")
        if not file_obj:
            return HttpResponse(status=420)
        file_obj.name = f"images/client/{client_uid}/{file_obj.name}"

        client.image = file_obj
        client.save()

        return HttpResponse(status=200)


@method_decorator(csrf_exempt, name="dispatch")
class SKUImageView(View):
    def delete(self, request, sku_uid, **kwargs):
        try:
            sku = SKU.objects.get(pk=sku_uid)
        except SKU.DoesNotExist:
            raise Http404
        sku.image = None
        sku.save()
        return HttpResponse(status=200)

    def post(self, request, sku_uid, **kwargs):
        try:
            sku = SKU.objects.get(pk=sku_uid)
        except SKU.DoesNotExist:
            raise Http404
        file_obj = request.FILES.get("image")
        if not file_obj:
            return HttpResponse(status=420)
        file_obj.name = f"images/sku/{sku_uid}/{file_obj.name}"

        sku.image = file_obj
        sku.save()

        return HttpResponse(status=200)


# DO NOT LEAVE THIS HERE --> FOR TESTING ONLY
@method_decorator(csrf_exempt, name="dispatch")
class FormTemplateView(View):
    def post(self, request, template_uid=None, **kwargs):
        file_obj = request.FILES.get("template_file")
        if not file_obj:
            return HttpResponse(status=420)
        name = request.POST.get("name", file_obj.name)
        try:
            template = FormTemplate.objects.get(pk=template_uid)
            template.template_file = file_obj
            template.name = template.name or request.POST.get("name", "")
            template.save()
        except FormTemplate.DoesNotExist:
            template = FormTemplate.objects.create(name=name, template_file=file_obj)
        try:
            template.write_parsed_annotations()
        except Exception:
            print("Failed to parse annotations...") # !!!
        return HttpResponse(template.template_file.url, status=200)
