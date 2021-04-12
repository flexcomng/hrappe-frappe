import frappe
from frappe import _
from frappe.utils import cint, get_formatted_email
from xml.etree import cElementTree as ElementTree
from binascii import a2b_base64
import base64

STANDARD_USERS = ("Guest", "Administrator")


def portal_settings():
    doc = frappe.get_doc("Portal App Settings", "Portal App Settings")
    return doc


def xml_to_dic(xml_string):
    root = ElementTree.XML(xml_string)
    xmldict = XmlDictConfig(root)
    return xmldict


class XmlDictConfig(dict):
    """
    Example usage:
    >>> tree = ElementTree.parse('your_file.xml')
    >>> root = tree.getroot()
    >>> xmldict = XmlDictConfig(root)
    Or, if you want to use an XML string:
    >>> root = ElementTree.XML(xml_string)
    >>> xmldict = XmlDictConfig(root)
    And then use xmldict for what it is... a dict.
    """

    def __init__(self, parent_element):
        if parent_element.items():
            self.update(dict(parent_element.items()))
        for element in parent_element:
            if element:
                # treat like dict - we assume that if the first two tags
                # in a series are different, then they are all different.
                if len(element) == 1 or element[0].tag != element[1].tag:
                    aDict = XmlDictConfig(element)
                # treat like list - we assume that if the first two tags
                # in a series are the same, then the rest are the same.
                else:
                    # here, we put the list in dictionary; the key is the
                    # tag name the list elements all share in common, and
                    # the value is the list itself
                    aDict = {element[0].tag: XmlListConfig(element)}
                # if the tag has attributes, add those to the dict
                if element.items():
                    aDict.update(dict(element.items()))
                self.update({element.tag.lower(): aDict})
            # this assumes that if you've got an attribute in a tag,
            # you won't be having any text. This may or may not be a
            # good idea -- time will tell. It works for the way we are
            # currently doing XML configuration files...
            elif element.items():
                self.update({element.tag: dict(element.items())})
            # finally, if there are no child tags and no attributes, extract
            # the text
            else:
                self.update({element.tag.lower(): element.text})


def update_password_reset_limit(user):
    generated_link_count = get_generated_link_count(user)
    generated_link_count += 1
    frappe.cache().hset("password_reset_link_count", user, generated_link_count)


def check_password_reset_limit(user, rate_limit):
    generated_link_count = get_generated_link_count(user)
    if generated_link_count >= rate_limit:
        frappe.throw(
            _(
                "You have reached the hourly limit for generating password reset links. Please try again later."
            )
        )


def get_generated_link_count(user):
    return cint(frappe.cache().hget("password_reset_link_count", user)) or 0


def reset_password(user, send_email=False, password_expired=False):
    from frappe.utils import random_string

    settings = portal_settings()

    rate_limit = frappe.db.get_single_value("System Settings", "password_reset_limit")

    if rate_limit:
        check_password_reset_limit(user.name, rate_limit)

        key = random_string(32)
        user.db_set("reset_password_key", key)

        url = "/update-password?key=" + key
        if password_expired:
            url = "/update-password?key=" + key + "&password_expired=true"

        link = settings.portal_url + url
        if send_email:
            password_reset_mail(user, link)

        update_password_reset_limit(user.name)
        return link


def password_reset_mail(user, link):
    send_login_mail(
        user, _("Password Reset"), "password_reset", {"link": link}, now=True
    )


def send_login_mail(user, subject, template, add_args, now=None):
    """send mail with login details"""
    from frappe.utils.user import get_user_fullname

    settings = portal_settings()

    full_name = get_user_fullname(frappe.session["user"])
    if full_name == "Guest":
        full_name = "Administrator"

    args = {
        "first_name": user.first_name or user.last_name or "user",
        "user": user.name,
        "title": subject,
        "login_url": settings.portal_url + "/login",
        "user_fullname": full_name,
    }

    args.update(add_args)

    sender = frappe.get_value("Email Account", settings.email, "email_id")
    if not sender:
        sender = (
            frappe.session.user not in STANDARD_USERS
            and get_formatted_email(frappe.session.user)
            or None
        )

    frappe.sendmail(
        recipients=user.email,
        sender=sender,
        subject=subject,
        template=template,
        args=args,
        header=[subject, "green"],
        delayed=(not now) if now != None else user.flags.delay_emails,
        retry=3,
    )


def send_welcome_mail_to_user(user):
    settings = portal_settings()
    link = reset_password(user)
    subject = None
    site_name = settings.portal_name
    if site_name:
        subject = _("Welcome to {0}").format(site_name)
    else:
        subject = _("Complete Registration")

    send_login_mail(
        user,
        subject,
        "new_user",
        dict(
            link=link,
            site_url=settings.portal_url,
        ),
    )


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


def add_file(file, fieldname, doctype, docname, file_name=None):
    file_name = file_name or frappe.utils.random_string(20) + ".png"
    if "," in file:
        file = file.split(",")[1]
    ret = frappe.get_doc(
        {
            "doctype": "File",
            "attached_to_doctype": doctype,
            "attached_to_name": docname,
            "attached_to_field": fieldname,
            "folder": "Home",
            "file_name": file_name,
            "file_url": "/files/" + file_name,
            "is_private": 0,
            "content": a2b_base64(file),
        }
    )
    ret.save(ignore_permissions=True)
    return ret.file_url


def to_base64(value):
    data_bytes = value.encode("ascii")
    data = base64.b64encode(data_bytes)
    return str(data)[2:-1]


def delete_file(doctype, docname, field_name):
    img_link = frappe.get_value(doctype, docname, field_name)
    if img_link:
        image_list = frappe.get_all(
            "File", filters={"file_name": img_link.split("/")[-1]}
        )
        if len(image_list) > 0:
            image = image_list[0]
            frappe.delete_doc("File", image.name)
            frappe.db.commit()
            return True
    return False
