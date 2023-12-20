// Copyright (c) 2023, Sudharsanan Ashok and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Transaction Report"] = {
	filters: [
		{
			reqd : 1,
			fieldname : "company_name",
			label : __("Comapny Name"),
			fieldtype : "Link",
			options : "Company",
			default : frappe.defaults.get_user_default("Company")
		},
		{
			"fieldname" : "filter_based_on",
			"label" : "Filter Based On",
			"fieldtype" : "Select",
			"options" : ["Fiscal Year","Date Range"],
			"default" : "Fiscal Year",
			"reqd" : 1,
			onchange:function(){
				let filter_based_on = frappe.query_report.get_filter_value("filter_based_on");
				frappe.query_report.toggle_filter_display('from_fiscal_year', filter_based_on === 'Date Range')
				frappe.query_report.toggle_filter_display('to_fiscal_year', filter_based_on === 'Date Range')
				frappe.query_report.toggle_filter_display('period_start_date', filter_based_on === 'Fiscal Year')
				frappe.query_report.toggle_filter_display('period_end_date', filter_based_on === 'Fiscal Year')

				frappe.query_report.refresh();
			}
		},
		{
			"fieldname":"period_start_date",
			"label": __("Start Date"),
			"fieldtype": "Date",
			"default" : frappe.datetime.add_months(frappe.datetime.get_today(), -1),
			"reqd": frappe.query_report.get_filter_value("filter_based_on") === 'Date Range',
			"depends_on": "eval:doc.filter_based_on == 'Date Range'"
		},
		{
			"fieldname" : "period_end_date",
			"label" : __("End Date"),
			"fieldtype" : "Date",
			"default" : frappe.datetime.get_today(),
			"reqd" : frappe.query_report.get_filter_value("filter_based_on") === 'Date Range',
			"depends_on" : "eval:doc.filter_based_on == 'Date Range'"
		},
		{
			"fieldname":"from_fiscal_year",
			"label": __("Start Year"),
			"fieldtype": "Link",
			"options": "Fiscal Year",
			"default": erpnext.utils.get_fiscal_year(frappe.datetime.get_today()),
			"reqd": !frappe.query_report.get_filter_value("filter_based_on") === 'Date Range',
			"depends_on": "eval:doc.filter_based_on == 'Fiscal Year'"
		},
		{
			"fieldname":"to_fiscal_year",
			"label": __("End Year"),
			"fieldtype": "Link",
			"options": "Fiscal Year",
			"default": erpnext.utils.get_fiscal_year(frappe.datetime.get_today()),
			"reqd": !frappe.query_report.get_filter_value("filter_based_on") === 'Date Range',
			"depends_on": "eval:doc.filter_based_on == 'Fiscal Year'"
		},
		{
			fieldname : "periodicity",
			label : __("periodicity"),
			fieldtype : "Select",
			options : ["Monthly", "Quarterly", "Half-Yearly", "Yearly"],
			default : "Yearly",
			reqd : 1
		},
		{
			fieldname : "party_type",
			label : __("Party Type"),
			fieldtype : "Link",
			options : "DocType",
			get_query : function(){
				return {
					filters : {
						name : ["in",["Supplier", "Customer"]]
					}
				}
			},
		},
		{
			fieldname : "party_id",
			label : __("Party ID"),
			fieldtype : "Dynamic Link",
			get_options : function(){
				let party_type = frappe.query_report.get_filter_value("party_type")
				if(!party_type){
					frappe.throw("First you have to enter the party type first")
				}
				return party_type
			}
		},
		{
			fieldname : "product_name",
			label : __("Product Name"),
			fieldtype : "Link",
			options : "Product List",
		},
		{
			fieldname : "invoice_doctype",
			label : __("Invoice DocType"),
			fieldtype : "Link",
			options : "DocType",
			get_query : function(){
				return {
					filters : {
						name : ["in", ["Purchase Invoices", "Sales Invoices"]]
					},
				};
			},
		},
		{
			fieldname : "invoice_id",
			label : __("Invoice ID"),
			fieldtype : "Dynamic Link",
			get_options : function(){
				let invoice_doctype = frappe.query_report.get_filter_value("invoice_doctype")
				if(!invoice_doctype){
					frappe.throw("First you have to enter the invoice doctype")
				}
				return invoice_doctype
			}
		}
	]
};
