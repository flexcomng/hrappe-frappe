// Copyright (c) 2021, Youssef Restom and contributors
// For license information, please see license.txt

frappe.ui.form.on('HR Employee Appraisal', {
	// refresh: function(frm) {

	// }
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