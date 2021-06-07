from django.shortcuts import render

from members.models import Department
from members.utils.user import user_to_person
from members.views.Activities import activity_lists, family_invites, participation


def departmentView(request, name):
    family = user_to_person(request.user).family
    department = Department.objects.get(name=name)

    return render(
        request,
        "members/department.html",
        {
            "department": department,
            "family": family,
            "invites": family_invites(family, department),
            "participating": participation(family, department),
            "open_activities": activity_lists(family, department),
        },
    )
