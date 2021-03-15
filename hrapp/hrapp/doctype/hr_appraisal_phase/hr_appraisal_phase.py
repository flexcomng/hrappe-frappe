# -*- coding: utf-8 -*-
# Copyright (c) 2021, Youssef Restom and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import date_diff, nowdate


class HRAppraisalPhase(Document):
    def validate(self):
        self.validate_dates()

    def on_submit(self):
        self.create_appraisals()

    def validate_dates(self):
        period_diff = date_diff(self.start, self.end)
        if period_diff >= 0:
            frappe.throw(
                _("The start date of the period should not be before the end date of the period"))

        end_diff = date_diff(nowdate(), self.end_date)
        if end_diff >= 0:
            frappe.throw(
                _("The Appraisal end date should not be earlier or the same as today"))

        end_period_diff = date_diff(self.end_date, self.end)
        if end_period_diff <= 0:
            frappe.throw(
                _("The end date of the Appraisal must be after the end date of the period"))

    def create_appraisals(self):
        filters = {"company": self.company, "status": "Active"}
        if self.department:
            filters["department"] = self.department
        employees = frappe.get_all("Employee", filters=filters)
        for emp in employees:
            if self.appraisal_type == "Employees":
                doc = frappe.new_doc("HR Employee Appraisal")
                doc.employee = emp.name
                doc.phase = self.name
                doc.template = self.template
                doc.save(ignore_permissions=True)
                frappe.msgprint(
                    _("New Appraisal is created for meployee {0}").format(emp.name), alert=True)
            elif self.appraisal_type == "Supervisors":
                doc = frappe.new_doc("HR Supervisor Appraisal Record")
                doc.employee = emp.name
                doc.phase = self.name
                doc.template = self.template
                doc.save(ignore_permissions=True)
                doc.submit()
                frappe.msgprint(
                    _("New Appraisal is created for meployee {0}").format(emp.name), alert=True)
