// Copyright (c) 2021, Youssef Restom and contributors
// For license information, please see license.txt

frappe.ui.form.on('HR Employee Appraisal', {
	onload: function (frm) {
		const jobs_employee_rating = frappe.meta.get_docfield("HR Employee Appraisal Job Details", "employee_rating", frm.doc.name);
		const jobs_manager_rating = frappe.meta.get_docfield("HR Employee Appraisal Job Details", "manager_rating", frm.doc.name);
		const jobs_panelist_rating = frappe.meta.get_docfield("HR Employee Appraisal Job Details", "panelist_rating", frm.doc.name);
		const performances_employee_rating = frappe.meta.get_docfield("HR Employee Appraisal Performance Details", "employee_rating", frm.doc.name);
		const performances_employee_comment = frappe.meta.get_docfield("HR Employee Appraisal Performance Details", "employee_comment", frm.doc.name);
		const performances_manager_rating = frappe.meta.get_docfield("HR Employee Appraisal Performance Details", "manager_rating", frm.doc.name);
		const performances_manager_comment = frappe.meta.get_docfield("HR Employee Appraisal Performance Details", "manager_comment", frm.doc.name);
		const performances_panelist_rating = frappe.meta.get_docfield("HR Employee Appraisal Performance Details", "panelist_rating", frm.doc.name);
		const performances_panelist_comment = frappe.meta.get_docfield("HR Employee Appraisal Performance Details", "panelist_comment", frm.doc.name);

		if (frappe.user.has_role("Panelist")) {
			jobs_panelist_rating.read_only = 0;
			performances_panelist_rating.read_only = 0;
			performances_panelist_comment.read_only = 0;
			frm.set_df_property("recommendation", "read_only", false);
		}
		if (frappe.user.name == frm.doc.emp_user) {
			jobs_employee_rating.read_only = 0;
			performances_employee_rating.read_only = 0;
			performances_employee_comment.read_only = 0;
			frm.set_df_property("jobs_employee_comments", "read_only", false);
			frm.set_df_property("employee_comment", "read_only", false);
		}
		if (frappe.user.name == frm.doc.man_user) {
			jobs_manager_rating.read_only = 0;
			performances_manager_rating.read_only = 0;
			performances_manager_comment.read_only = 0;
			frm.set_df_property("jobs_manager_comment", "read_only", false);
			frm.set_df_property("manager_comment", "read_only", false);
		}
		frm.refresh_field("jobs");
		frm.refresh_field("jperformancesobs");
	}
});

frappe.ui.form.on('HR Employee Appraisal Job Details', {
	jobs_add: (frm, cdt, cdn) => {
		control_rows(frm, cdt, cdn);
	},
	jobs_remove: (frm, cdt, cdn) => {
		control_rows(frm, cdt, cdn);
	},
});
frappe.ui.form.on('HR Employee Appraisal Performance Details', {
	performances_add: (frm, cdt, cdn) => {
		control_rows(frm, cdt, cdn);
	},
	performances_remove: (frm, cdt, cdn) => {
		control_rows(frm, cdt, cdn);
	},
});



const control_rows = (frm, cdt, cdn) => {
	// let row = frappe.get_doc(cdt, cdn);
	// frm.reload_doc();
	frappe.throw(__(`This line should not add or delete it`));
};