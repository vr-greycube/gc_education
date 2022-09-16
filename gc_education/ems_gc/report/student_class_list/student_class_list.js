// Copyright (c) 2022, Greycube and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Student Class List"] = {
	"filters": [
		{ "label": "Academic Year", "fieldname": "academic_year", "fieldtype": "Link", "options": "Academic Year", },
		{ "label": "Academic Term", "fieldname": "academic_term", "fieldtype": "Link", "options": "Academic Term", },
		{
			"fieldname": "department",
			"label": __("Department"),
			"fieldtype": "MultiSelectList",
			get_data: function (txt) {
				return frappe.db.get_link_options('Department', txt);
			}
		},
		{
			"fieldname": "program",
			"label": __("Class"),
			"fieldtype": "MultiSelectList",
			get_data: function (txt) {
				return frappe.db.get_link_options('Program', txt);
			}
		},
		{
			"fieldname": "batch",
			"label": __("Division"),
			"fieldtype": "MultiSelectList",
			get_data: function (txt) {
				return frappe.db.get_link_options('Student Batch Name', txt);
			}
		},
		{
			"fieldname": "as_on_date",
			"label": __("As on Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
			"reqd": 1
		},
		{
			"label": "Student Status", "fieldname": "student_status",
			"fieldtype": "Select", "options": "All\nEnabled\nDisabled",
			"default": "Enabled",
		},

	],
	onload: function (report) {
		// set_options()
	}
};
