# -*- coding: utf-8 -*-
# Copyright (c) 2021, Youssef Restom and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from hrapp.api.utlis import generate_response
from erpnext.hr.doctype.leave_application.leave_application import get_leave_balance_on, get_leaves_for_period, get_pending_leaves_for_period, get_leave_allocation_records, get_leave_approver


def get_login_employee():
    user = str(frappe.session.user)
    employees = frappe.get_all(
        "Employee", filters={"user_id": user, "status": "Active"})
    if len(employees) > 0:
        return employees[0].name


@ frappe.whitelist()
def get_doc(doctype=None, docname=None, fieldname=None):
    if not doctype:
        return generate_response("F", error="'doctype' parameter is required")
    if not docname:
        return generate_response("F", error="'docname' parameter is required")

    try:
        if not frappe.has_permission(doctype, "read"):
            frappe.local.response.http_status_code = 403
            return generate_response("F", "403", error="Access denied")
        if not frappe.db.exists(doctype, docname):
            frappe.local.response.http_status_code = 404
            return generate_response("F", "404", error="{0} '{1}' not exist".format(doctype, docname))
        doc = frappe.get_doc(doctype, docname)
        employee = get_login_employee()
        field = 'employee' if not fieldname else fieldname
        if doc.get(field) != employee:
            frappe.local.response.http_status_code = 403
            return generate_response("F", "403", error="Access denied")
        return generate_response("S", "200", message="Success", data=doc)
    except Exception as e:
        return generate_response("F", error=e)


@frappe.whitelist()
def get_leave_details(employee=None, date=None):
    if not employee:
        return generate_response("F", error="'employee' parameter is required")
    if not date:
        return generate_response("F", error="'date' parameter is required")
    try:
        allocation_records = get_leave_allocation_records(employee, date)
        leave_allocation = {}
        for d in allocation_records:
            allocation = allocation_records.get(d, frappe._dict())

            total_allocated_leaves = frappe.db.get_value('Leave Allocation', {
                'from_date': ('<=', date),
                'to_date': ('>=', date),
                'employee': employee,
                'leave_type': allocation.leave_type,
            }, 'SUM(total_leaves_allocated)') or 0

            remaining_leaves = get_leave_balance_on(employee, d, date, to_date=allocation.to_date,
                                                    consider_all_leaves_in_the_allocation_period=True)

            end_date = allocation.to_date
            leaves_taken = get_leaves_for_period(
                employee, d, allocation.from_date, end_date) * -1
            leaves_pending = get_pending_leaves_for_period(
                employee, d, allocation.from_date, end_date)

            leave_allocation[d] = {
                "total_leaves": total_allocated_leaves,
                "expired_leaves": total_allocated_leaves - (remaining_leaves + leaves_taken),
                "leaves_taken": leaves_taken,
                "pending_leaves": leaves_pending,
                "remaining_leaves": remaining_leaves}

        # is used in set query
        lwps = frappe.get_list("Leave Type", filters={"is_lwp": 1})
        lwps = [lwp.name for lwp in lwps]

        ret = {
            'leave_allocation': leave_allocation,
            'leave_approver': get_leave_approver(employee),
            'lwps': lwps
        }
        generate_response("S", "200", message="Success", data=ret)

    except Exception as e:
        return generate_response("F", error=e)


@frappe.whitelist()
def get_training_events(employee):
    if not employee:
        return generate_response("F", error="'employee' parameter is required")
    try:
        events = frappe.get_all("Training Event Employee",
                                filters={
                                    "employee": employee,
                                    "docstatus": 1
                                },
                                fields=["parent"]
                                )
        events_list = []
        for event in events:
            if event.parent not in events_list:
                events_list.append(event.parent)

        training_events = frappe.get_all("Training Event",
                                         filters={
                                             "name": ["in", events_list],
                                             "docstatus": 1
                                         },
                                         fields=["*"]
                                         )
        generate_response("S", "200", message="Success", data=training_events)

    except Exception as e:
        return generate_response("F", error=e)


@frappe.whitelist()
def get_training_results(employee):
    if not employee:
        return generate_response("F", error="'employee' parameter is required")
    try:
        results = frappe.get_all("Training Result Employee",
                                 filters={
                                     "employee": employee,
                                     "docstatus": 1
                                 },
                                 fields=[
                                     "parent as name", "parenttype as doctype", "employee", "employee_name", "department", "hours", "grade", "comments"]
                                 )
        for item in results:
            item["training_event"] = frappe.get_value(
                "Training Result", item.name, "training_event")
        generate_response("S", "200", message="Success", data=results)

    except Exception as e:
        return generate_response("F", error=e)
