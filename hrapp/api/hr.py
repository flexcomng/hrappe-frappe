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


@ frappe.whitelist()
def get_doc(doctype=None, docname=None):
    if not doctype:
        return generate_response("F", error="'doctype' parameter is required")
    if not docname:
        return generate_response("F", error="'docname' parameter is required")

    try:
        if not frappe.db.exists(doctype, docname):
            frappe.local.response.http_status_code = 404
            return generate_response("F", "404", error="{0} '{1}' not exist".format(doctype, docname))
        doc = frappe.get_doc(doctype, docname)
        employee = get_login_employee()

        if doc.employee != employee:
            return generate_response("F", "403", error="Access denied")
        return generate_response("S", "200", message="Success", data=doc)
    except Exception as e:
        return generate_response("F", error=e)
