from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("orco_ofx_to_qbo_ofx", views.orco_ofx_to_qbo_ofx_view, name="orco_ofx_to_qbo_ofx"),
    path("mcb_ofx_to_qbo_ofx", views.mcb_ofx_to_qbo_ofx_view, name="mcb_ofx_to_qbo_ofx"),
    path("rabo_csv_to_qbo_ofx", views.rabo_csv_to_qbo_ofx_view, name="rabo_csv_to_qbo_ofx"),

    path("download/<uuid:cache_id>", views.download, name="download"),

]
