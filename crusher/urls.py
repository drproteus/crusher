"""crusher URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import TemplateView

from graphene_django.views import GraphQLView
import app.views

urlpatterns = [
    path("graphql", GraphQLView.as_view(graphiql=True)),
    path(
        "upload/invoice-attachment/<uuid:invoice_uid>",
        app.views.InvoiceAttachmentView.as_view(),
    ),
    path(
        "upload/contact-attachment/<uuid:contact_uid>",
        app.views.ContactAttachmentView.as_view(),
    ),
    path(
        "upload/client-attachment/<uuid:client_uid>",
        app.views.ClientAttachmentView.as_view(),
    ),
    path("upload/client-image/<uuid:client_uid>", app.views.ClientImageView.as_view(),),
    path(
        "upload/contact-image/<uuid:contact_uid>", app.views.ContactImageView.as_view(),
    ),
    path("upload/sku-image/<uuid:sku_uid>", app.views.SKUImageView.as_view()),
    path("upload/attachment/<uuid:attachment_uid>", app.views.AttachmentView.as_view()),
    path("upload/form-template", app.views.FormTemplateView.as_view()),
    path("upload/form-template/<uuid:template_uid>", app.views.FormTemplateView.as_view()),
    re_path(".*", TemplateView.as_view(template_name="app/index.html")),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
