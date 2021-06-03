from django.shortcuts import render

from members.models import Department


def departmentView(request, name):
    return render(
        request,
        "members/department.html",
        {"department": Department.objects.get(name=name)},
    )
