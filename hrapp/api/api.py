# -*- coding: utf-8 -*-
# Copyright (c) 2021, Youssef Restom and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
import json
from frappe.utils.pdf import get_pdf
from erpnext.accounts.doctype.payment_entry.payment_entry import get_payment_entry
from frappe.utils import nowdate, getdate, cint, today
import requests
from hrapp.api.utlis import xml_to_dic, send_welcome_mail_to_user, reset_password
from frappe.utils.password import update_password as _update_password


@ frappe.whitelist()
def get_user():
    user = frappe.session.user
    user_doc = frappe.get_doc("User", user)
    return user_doc


@ frappe.whitelist()
def get_doc(doctype, docname):
    if not frappe.db.exists(doctype, docname):
        return {}
    doc = frappe.get_doc(doctype, docname)
    return doc


@ frappe.whitelist()
def update_doc(doctype, doc, docname=None, action="Save"):
    doc = json.loads(doc)
    if not docname or not frappe.db.exists(doctype, docname):
        doc["name"] = ""
        cur_doc = frappe.new_doc(doctype)
    else:
        cur_doc = frappe.get_doc(doctype, docname)
    cur_doc.flags.ignore_permissions = True
    cur_doc.update(doc)
    cur_doc.save(ignore_permissions=True)
    if action == "Submit":
        cur_doc.submit()
    cur_doc.reload()
    return cur_doc


@ frappe.whitelist()
def get_all(doctype, fields=None, filters=None, order_by=None, group_by=None, start=None, page_length=None):
    if not fields:
        fields = ["*"]
    else:
        fields = json.loads(fields)
    if not filters:
        filters = {}
    else:
        filters = json.loads(filters)
    return frappe.get_all(doctype, fields, filters, order_by, group_by, start, page_length)


@ frappe.whitelist(allow_guest=True)
def get_items():
    items = frappe.get_all("Item", filters={"disabled": False}, fields=["*"])
    return items


@ frappe.whitelist(allow_guest=True)
def get_groups():
    groups = frappe.get_all("Item Base Group")
    for item in groups:
        item.active = False
        item.sub_groups = []
        item.sub_groups = frappe.get_all(
            "Item Sub Group", filters={"base_group": item.name})
    return groups


@ frappe.whitelist(allow_guest=True)
def get_settings():
    doc = frappe.get_doc("HRapp Settings", "HRapp Settings")
    return doc


@ frappe.whitelist(allow_guest=True)
def get_item(docname):
    if not frappe.db.exists("Item", docname):
        return {}
    doc = frappe.get_doc("Item", docname)
    return doc


@ frappe.whitelist()
def get_pdf_file(doctype, docname):
    print_format = ""
    default_print_format = frappe.db.get_value('Property Setter', dict(
        property='default_print_format', doc_type=doctype), "value")
    if default_print_format:
        print_format = default_print_format
    else:
        print_format = "Standard"

    html = frappe.get_print(
        doctype, docname, print_format, doc=None, no_letterhead=0)
    frappe.local.response.filename = "{name}.pdf".format(
        name=docname.replace(" ", "-").replace("/", "-"))
    frappe.local.response.filecontent = get_pdf(html)
    frappe.local.response.type = "pdf"


@ frappe.whitelist()
def make_payment_si(docname, ref_type, ref_no, amount=None, power_data=None):
    payment_doc = get_payment_entry(
        "Sales Invoice", docname)
    payment_doc.update({
        "mode_of_payment": ref_type,
        "reference_no": ref_no,
        "reference_date": nowdate(),
    })
    if amount:
        payment_doc.update({
            "paid_amount": float(amount),
            "received_amount": float(amount),
        })
    if power_data:
        payment_doc.update({
            "power_data": str(power_data),
        })

    payment_doc.set_amounts()
    payment_doc.setup_party_account_field()
    payment_doc.flags.ignore_permissions = True
    frappe.flags.ignore_account_permission = True
    payment_doc.save(ignore_permissions=True)
    payment_doc.submit()
    frappe.db.commit()
    return payment_doc.name


def create_sales_invoice(customer, ammount, qty, ref_no):
    settings = get_settings()
    sales_invoice = frappe.new_doc('Sales Invoice')
    sales_invoice.customer = customer
    sales_invoice.remarks = "Power Token: " + ref_no
    sales_invoice.due_date = getdate()
    sales_invoice.company = settings.company
    sales_invoice.type = "Power"
    item = frappe.get_doc("Item", "Electricity")

    sales_invoice.append('items', {
        'item_code': item.item_code,
        'item_name': item.item_name,
        'description': item.description,
        'qty': float(qty),
        'uom': 'Unit',
        'conversion_factor': 1,
        'rate': float(ammount) / float(qty),
        'amount': float(ammount)
    })

    sales_invoice.flags.ignore_permissions = True
    frappe.flags.ignore_account_permission = True
    sales_invoice.set_missing_values()
    sales_invoice.save(ignore_permissions=True)

    sales_invoice.submit()
    return sales_invoice.name


@ frappe.whitelist(allow_guest=True)
def test_password_strength(new_password, user_data=None):
    from frappe.utils.password_strength import test_password_strength as _test_password_strength

    password_policy = frappe.db.get_value("System Settings", None,
                                          ["enable_password_policy", "minimum_password_score"], as_dict=True) or {}

    enable_password_policy = cint(
        password_policy.get("enable_password_policy", 0))
    minimum_password_score = cint(
        password_policy.get("minimum_password_score", 0))

    if not enable_password_policy:
        return {}

    if not user_data:
        user_data = frappe.db.get_value('User', frappe.session.user,
                                        ['first_name', 'middle_name', 'last_name', 'email', 'birth_date'])

    if new_password:
        result = _test_password_strength(new_password, user_inputs=user_data)
        password_policy_validation_passed = False

        # score should be greater than 0 and minimum_password_score
        if result.get('score') and result.get('score') >= minimum_password_score:
            password_policy_validation_passed = True

        result['feedback']['password_policy_validation_passed'] = password_policy_validation_passed
        return result


def handle_password_test_fail(result):
    suggestions = result['feedback']['suggestions'][0] if result['feedback']['suggestions'] else ''
    warning = result['feedback']['warning'] if 'warning' in result['feedback'] else ''
    suggestions += "<br>" + \
        _("Hint: Include symbols, numbers and capital letters in the password") + '<br>'
    frappe.throw(' '.join([_('Invalid Password:'), warning, suggestions]))


@ frappe.whitelist()
def update_password(new_password):
    result = test_password_strength(new_password)
    feedback = result.get("feedback", None)

    if feedback and not feedback.get('password_policy_validation_passed', False):
        handle_password_test_fail(result)

    user = frappe.session.user

    _update_password(user, new_password)

    frappe.local.login_manager.login_as(user)

    frappe.db.set_value("User", user, "last_password_reset_date", today())
    frappe.db.set_value("User", user, "reset_password_key", "")


def send_welcome_mail(doc, method):
    if doc.is_new and doc.send_cust_welcome_email:
        send_welcome_mail_to_user(doc)


@ frappe.whitelist(allow_guest=True)
def reset_pass(user):
    if user == "Administrator":
        return 'not allowed'

    try:
        user = frappe.get_doc("User", user)
        if not user.enabled:
            return 'disabled'

        user.validate_reset_password()
        reset_password(user, send_email=True)

        return frappe.msgprint(_("Password reset instructions have been sent to your email"))

    except frappe.DoesNotExistError:
        frappe.clear_messages()
        return 'User not found'
