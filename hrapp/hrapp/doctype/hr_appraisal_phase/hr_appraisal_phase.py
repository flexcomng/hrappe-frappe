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
