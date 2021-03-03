# -*- coding: utf-8 -*-
# Copyright (c) 2021, Youssef Restom and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document


class HREmployeeAppraisal(Document):
    def before_insert(self):
        if not self.template:
            return
        template = frappe.get_doc("HR Appraisal Template", self.template)
        for el in template.jobs:
            row = self.append('jobs', {})
            row.title = el.title
            row.description = el.description
        for el in template.performances:
            row = self.append('performances', {})
            row.title = el.title
            row.description = el.description
