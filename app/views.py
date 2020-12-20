from datetime import datetime
from uuid import uuid4

from django.core.files.storage import default_storage
from django.shortcuts import Http404, HttpResponse, render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from app.models import Attachment, Invoice


class FilenameConflictException(Exception):
    pass


# DO NOT LEAVE THIS HERE --> FOR TESTING ONLY
@method_decorator(csrf_exempt, name="dispatch")
class UploadInvoiceAttachmentView(View):
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
        name = request.POST.get(
            "filename",
            f"Invoice Attachment [{datetime.now().isoformat()}] {file_obj.name}",
        )
        file_obj.name = name
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
