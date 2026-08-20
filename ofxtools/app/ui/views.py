import json
import uuid
from pathlib import Path

from django.core.cache import cache
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.template import loader
from . import orco_ofx_to_qbo_ofx, rabo_csv_to_qbo_ofx, mcb_ofx_to_qbo_ofx, orcomerch_xlsx_to_qbo_ofx


# Create your views here.
def index(request):
    template = loader.get_template("index.html")
    context = {}
    return HttpResponse(template.render(context, request))


def over(request):
    template = loader.get_template("over.html")
    context = {}
    return HttpResponse(template.render(context, request))


def orco_ofx_to_qbo_ofx_view(request):
    if request.method == 'POST' and request.FILES['myfile']:
        myfile = request.FILES['myfile']

        filename = myfile.name
        myfile_bytes = myfile.read()
        myfile_text = myfile_bytes.decode("utf-8")

        o = orco_ofx_to_qbo_ofx.convert(myfile_text)
        new_id = uuid.uuid4()
        cache.set(f"{new_id}_content", o, 600)
        cache.set(f"{new_id}_filename", filename, 600)

        return HttpResponseRedirect(f'/download/{new_id}')

    return render(request, 'orco_ofx_to_qbo_ofx.html')


def orcomerch_xlsx_to_qbo_ofx_view(request):
    if request.method == 'POST' and request.FILES['myfile']:
        myfile = request.FILES['myfile']

        filename = myfile.name
        myfile_bytes = myfile.read()

        o = orcomerch_xlsx_to_qbo_ofx.convert(filename, myfile_bytes)
        new_id = uuid.uuid4()
        cache.set(f"{new_id}_content", o, 600)
        cache.set(f"{new_id}_filename", filename, 600)

        return HttpResponseRedirect(f'/download/{new_id}')

    return render(request, 'orcomerch_xlsx_to_qbo_ofx.html')



def mcb_ofx_to_qbo_ofx_view(request):
    if request.method == 'POST' and request.FILES['myfile']:
        myfile = request.FILES['myfile']

        filename = myfile.name
        myfile_bytes = myfile.read()
        myfile_text = myfile_bytes.decode("utf-8")

        o = mcb_ofx_to_qbo_ofx.convert(myfile_text)
        new_id = uuid.uuid4()
        cache.set(f"{new_id}_content", o, 600)
        cache.set(f"{new_id}_filename", filename, 600)

        return HttpResponseRedirect(f'/download/{new_id}')

    return render(request, 'mcb_ofx_to_qbo_ofx.html')


def rabo_csv_to_qbo_ofx_view(request):
    if request.method == 'POST' and request.FILES['myfile']:
        myfile = request.FILES['myfile']

        filename = myfile.name
        myfile_bytes = myfile.read()
        myfile_text = myfile_bytes.decode('cp1252')

        o = rabo_csv_to_qbo_ofx.convert(myfile_text)
        new_id = uuid.uuid4()
        cache.set(f"{new_id}_content", o, 600)
        cache.set(f"{new_id}_filename", filename, 600)

        return HttpResponseRedirect(f'/download/{new_id}')

    return render(request, 'rabo_csv_to_qbo_ofx.html')


def download(request, cache_id):
    content = cache.get(f"{cache_id}_content")
    original_filename = cache.get(f"{cache_id}_filename")

    original_filename_without_ext = Path(original_filename).stem
    new_filename = f"{original_filename_without_ext}-qbo.ofx"
    response = HttpResponse(content, content_type='application/x-ofx')
    response['Content-Disposition'] = f"attachment; filename={new_filename}"
    return response
