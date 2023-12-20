// Copyright (c) 2023, Sudharsanan Ashok and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Stock Movement Report"] = {
	"filters": [
		{
			reqd: 1,
			fieldname: "reference_doctype",
			label: __("Entity Type"),
			fieldtype: "Link",
			options: "DocType",
			get_query: function () {
				return {
					filters: {
						name: ["in", "Stock Movement"],
					},
				};
			},
		},
		{
			fieldname: "reference_name",
			label: __("Entity Name"),
			fieldtype: "Dynamic Link",
			get_options: function () {
				let reference_doctype = frappe.query_report.get_filter_value("reference_doctype");
				if (!reference_doctype) {
					frappe.throw(__("Please select Entity Type first"));
				}
				return reference_doctype;
			},
		},
	]
};
