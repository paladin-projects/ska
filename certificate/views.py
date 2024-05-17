from django.http import HttpResponse
from django.shortcuts import render, redirect

from .models import *


# Create your views here.

def main(request):
    if request.method == 'GET':
        return render(request, "certificate.html")
    elif request.method == 'POST':
        data = request.POST
        print(data)
        obj = Certificate(employee_name=data.get("name"),
                          training_name=data.get("training_name"),
                          training_type=data.get("training_type"),
                          date=data.get("date"),
                          category=CertificateCategory.objects.get(category=data.get("category")),
                          certificate_file=request.FILES["certificate"])
        # tmp = data.get("date").split("-")
        # obj.date = f"{tmp[2]}-{tmp[1]}-{tmp[0]}"
        if data.get("subcategory", -1) != -1:
            obj.sub_category = CertificateSubCategory.objects.get(subcategory=data.get("subcategory"))

        obj.save()
        # with open("D\\:data", "wb+") as destination:
        #     for chunk in f.chunks():
        #         destination.write(chunk)
        return redirect('/')
