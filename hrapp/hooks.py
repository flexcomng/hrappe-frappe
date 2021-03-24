# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "hrapp"
app_title = "HRapp"
app_publisher = "Youssef Restom"
app_description = "HR Portal Plus Appraisal customization"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "youssef@totrox.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/hrapp/css/hrapp.css"
# app_include_js = "/assets/hrapp/js/hrapp.js"

# include js, css files in header of web template
# web_include_css = "/assets/hrapp/css/hrapp.css"
# web_include_js = "/assets/hrapp/js/hrapp.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "hrapp/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "hrapp.install.before_install"
# after_install = "hrapp.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "hrapp.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
    "User": {
        "after_insert": "hrapp.api.api.send_welcome_mail",
    }
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"hrapp.tasks.all"
# 	],
# 	"daily": [
# 		"hrapp.tasks.daily"
# 	],
# 	"hourly": [
# 		"hrapp.tasks.hourly"
# 	],
# 	"weekly": [
# 		"hrapp.tasks.weekly"
# 	]
# 	"monthly": [
# 		"hrapp.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "hrapp.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "hrapp.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "hrapp.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

fixtures = [
    {"doctype": "Custom Field", "filters": [["name", "in", (
        "User-send_emp_welcome_email",
    )]]},
    {"doctype": "Property Setter", "filters": [["name", "in", (
        "User-send_welcome_email-default",
    )]]},
    {"doctype": "Custom DocPerm", "filters": [["name", "in", (
        "acc1d831e9",
        "c91fbba028",
        "a2a3bf0a48",
        "f5531816ad"
    )]]},

    {"doctype": "Desk Page", "filters": [["name", "in", (
        "HR",
    )]]},

    {"doctype": "Role", "filters": [["name", "in", (
        "Panelist",
    )]]},
]
