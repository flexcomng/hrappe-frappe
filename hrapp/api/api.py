# -*- coding: utf-8 -*-
# Copyright (c) 2021, Youssef Restom and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.auth import LoginManager
import uuid
import json
from frappe.utils.pdf import get_pdf
from erpnext.accounts.doctype.payment_entry.payment_entry import get_payment_entry
from frappe.utils import nowdate, getdate, cint, today
import requests
from hrapp.api.utlis import xml_to_dic, send_welcome_mail_to_user, reset_password, to_base64, add_image, delete_image
from frappe.utils.password import update_password as _update_password


@frappe.whitelist(allow_guest=True)
def login(usr, pwd):
    try:
        login_manager = LoginManager()
        login_manager.authenticate(usr, pwd)
        login_manager.post_login()
        if frappe.response['message'] == 'Logged In':
            frappe.response['user'] = login_manager.user
            frappe.response['token'] = generate_key(login_manager.user)
    except Exception as e:
        return generate_response("F", error=e)

def generate_key(user):
    """
    generate api key and api secret
    :param user: str
    """
    user_details = frappe.get_doc("User", user)
    # if api key is not set generate api key
    if not user_details.api_key:
        api_key = frappe.generate_hash(length=15)
        user_details.api_key = api_key
    if not user_details.api_secret:
        api_secret = frappe.generate_hash(length=15)
        user_details.api_secret = api_secret
    user_details.save()
    api_kyes_base64 = to_base64(user_details.api_key+":"+user_details.api_key)
    token = "'Authorization': 'Basic {0}'".format(api_kyes_base64)
    return token


@frappe.whitelist()
def generate_response(_type, status=None, message=None, data=None, error=None):
    if _type == "S":
        if status:
            frappe.response["status_code"] = int(status)
        else:
            frappe.response["status_code"] = 200
        frappe.response["msg"] = message
        frappe.response["data"] = data
    else:
        frappe.log_error(frappe.get_traceback())
        if status:
            frappe.response["status_code"] = status
        else:
            frappe.response["status_code"] = 500
        if message:
            frappe.response["msg"] = message
        elif error:
            frappe.response["msg"] = str(error)
        else:
            frappe.response["msg"] = "Something Went Wrong"
        if error:
            frappe.response["error"] = error
        frappe.response["data"] = None


@ frappe.whitelist()
def get_user():
    try:
        user = frappe.session.user
        user_doc = frappe.get_doc("User", user)
        return generate_response("S", "200", message="Success", data=user_doc)
    except Exception as e:
        return generate_response("F", error=e)


@ frappe.whitelist()
def get_doc(doctype, docname):
    if not frappe.db.exists(doctype, docname):
        frappe.local.response.http_status_code = 404
        return generate_response("F", "404", error="{0} '{1}' not exist".format(doctype, docname))
    doc = frappe.get_doc(doctype, docname)
    return generate_response("S", "200", message="Success", data=doc)


@ frappe.whitelist()
def get_meta(doctype):
    try:
        data = frappe.get_meta(doctype)
        generate_response("S", "200", message="Success", data=data)
    except Exception:
        frappe.local.response.http_status_code = 404
        return generate_response("F", "404", error="{0} not exist".format(doctype))


@ frappe.whitelist()
def get_doc_meta(doctype, docname):
    if not frappe.db.exists(doctype, docname):
        frappe.local.response.http_status_code = 404
        return generate_response("F", "404", error="{0} '{1}' not exist".format(doctype, docname))
    doc = frappe.get_doc(doctype, docname)
    meta = frappe.get_meta(doctype)
    data = {
        "doc": doc,
        "meta": meta
    }
    return generate_response("S", "200", message="Success", data=data)


@ frappe.whitelist()
def update_doc(doc, doctype=None, docname=None, action="Save"):
    try:
        cur_doc = None
        status = None
        if not doc.get("doctype") and doctype:
            doc["doctype"] = doctype
        if not doc.get("name") and docname:
            doc["name"] = docname
        if frappe.db.exists(doc.get("doctype"), doc.get("name")):
            cur_doc = frappe.get_doc(doc.get("doctype"), doc.get("name"))
            status = "Updated"
        else:
            doc["name"] = ""
            cur_doc = frappe.new_doc(doc.get("doctype"))
            status = "Created"
        if not cur_doc:
            return generate_response("F")
        cur_doc.flags.ignore_permissions = True
        cur_doc.update(doc)
        cur_doc.save(ignore_permissions=True)
        if action == "Submit":
            cur_doc.submit()
        frappe.db.commit()
        return generate_response("S", "200", message="{0}: '{1}' {2} Successfully".format(cur_doc.doctype,cur_doc.name,status), data=cur_doc)
    except Exception as e:
        return generate_response("F", error=e)  


@ frappe.whitelist()
def get_all(doctype, fields=None, filters=None, order_by=None, group_by=None, start=None, page_length=None):
    try:
        if not fields:
            fields = ["*"]
        else:
            fields = json.loads(fields)
        if not filters:
            filters = {}
        else:
            filters = json.loads(filters)
        data = frappe.get_all(doctype, fields, filters, order_by, group_by, start, page_length)
        return generate_response("S", "200", message="Success", data=data)
    except Exception as e:
        return generate_response("F", error=e)  


@ frappe.whitelist(allow_guest=True)
def get_settings():
    try:    
        doc = frappe.get_doc("HRapp Settings", "HRapp Settings")
        return generate_response("S", "200", message="Success", data=doc)
    except Exception as e:
        return generate_response("F", error=e)


@ frappe.whitelist(allow_guest=True)
def get_item(docname):
    if not frappe.db.exists("Item", docname):
        return generate_response("F", error="Item not exist")  
    doc = frappe.get_doc("Item", docname)
    return generate_response("S", "200", message="Success", data=doc)


@ frappe.whitelist()
def get_pdf_file(doctype, docname):
    try:
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
    except Exception as e:
        return generate_response("F", error=e)


@ frappe.whitelist()
def make_payment_si(docname, ref_type, ref_no, amount=None, power_data=None):
    try:
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
        return generate_response("S", "200", message="Success", data=payment_doc.name)
    except Exception as e:
        return generate_response("F", error=e)


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
    try:
        result = test_password_strength(new_password)
        feedback = result.get("feedback", None)

        if feedback and not feedback.get('password_policy_validation_passed', False):
            handle_password_test_fail(result)

        user = frappe.session.user

        _update_password(user, new_password)

        frappe.local.login_manager.login_as(user)

        frappe.db.set_value("User", user, "last_password_reset_date", today())
        frappe.db.set_value("User", user, "reset_password_key", "")
    except Exception as e:
        return generate_response("F", error=e)


def send_welcome_mail(doc, method):
    if doc.is_new and doc.send_cust_welcome_email:
        send_welcome_mail_to_user(doc)


@ frappe.whitelist(allow_guest=True)
def reset_pass(user):
    try:
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
    except Exception as e:
        return generate_response("F", error=e)

@ frappe.whitelist()
def upload_image(doctype, docname, field_name, image):
    try:
        exists = frappe.db.exists(doctype, docname)
        if not exists:
            return generate_response("F", "404", error="Doctype {0} is not exist".format(docname))
        delete_image(doctype, docname, field_name)
        image_link = add_image(
            image, 'image', doctype, docname)

        frappe.set_value(doctype, docname, field_name, image_link)
        frappe.db.commit()
        if image_link:
            return generate_response("S", "200", message="Image Added Successfully", data=image_link)
    except Exception as e:
        return generate_response("F", error=e)
