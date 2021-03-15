# -*- coding: utf-8 -*-
# Copyright (c) 2021, Youssef Restom and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
# import frappe
from frappe.model.document import Document
from frappe.utils import flt


class HRSupervisorAppraisal(Document):
    def validate(self):
        self.set_totals()

    def set_totals(self):
        jobs_count = len(self.jobs)
        self.job_total = 0

        if jobs_count > 0:
            for row in self.jobs:
                self.job_total += flt(row.employee_rating)
            self.job_average = self.job_total / jobs_count

        performances_count = len(self.performances)
        self.performance_total = 0
        if performances_count > 0:
            for elm in self.performances:
                self.performance_total += flt(elm.employee_rating)
            self.performance_average = self.performance_total / performances_count

        self.total = self.job_total + self.performance_total
        self.average = (
            self.job_average + self.performance_average) / 2
