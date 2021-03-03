// Copyright (c) 2021, Youssef Restom and contributors
// For license information, please see license.txt

frappe.ui.form.on('HR Appraisal Phase', {
	setup: function (frm) {
		frm.set_query('department', function () {
			return {
				filters: {
					'company': frm.doc.company,
					'is_group': 0,
				}
			};
		});
	}
});
