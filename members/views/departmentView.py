from django.shortcuts import render

from members.models import Department
from members.views.Activities import activity_lists


def departmentView(request, name):
    department = Department.objects.get(name=name)

    family, invites, open_activities_with_persons, participating = activity_lists(
        request.user, department
    )

    return render(
        request,
        "members/department.html",
        {
            "department": department,
            "family": family,
            "invites": invites,
            "participating": participating,
            "open_activities": open_activities_with_persons,
        },
    )
