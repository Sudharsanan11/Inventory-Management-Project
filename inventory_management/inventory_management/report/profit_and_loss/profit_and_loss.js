// Copyright (c) 2023, Sudharsanan Ashok and contributors
// For license information, please see license.txt
/* eslint-disable */

// frappe.require("apps/inventory_management/inventory_management/inventory_management/report/transaction_report/transaction_report.js", function(){
// 	frappe.query_reports["Profit and Loss"] = $.extends({},
// 		inventory_management.transaction_report);

// 		erpnext.utils.add_dimensions('Profit and Loss', 10)
// })

frappe.query_reports["Profit and Loss"] = {
	"filters": [
		{
			reqd : 1,
			fieldname : "company_name",
			label : __("Comapny Name"),
			fieldtype : "Link",
			options : "Company",
			default : frappe.defaults.get_user_default("Company")
		},
		{
			fieldname : "from_date",
			label : __("From Date"),
			fieldtype : "Date",
			default : frappe.datetime.add_months(frappe.datetime.get_today(), -1),
			reqd : 1
		},
		{
			fieldname : "to_date",
			label : __("To Date"),
			fieldtype : "Date",
			default : frappe.datetime.get_today(),
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
