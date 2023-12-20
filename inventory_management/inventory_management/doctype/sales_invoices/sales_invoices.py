# Copyright (c) 2023, Sudharsanan Ashok and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import date

class SalesInvoices(Document):
	def before_save(self):
		self.check_quantity()


	def check_quantity(self):
		for i in self.items:
			exists = frappe.db.exists(
				"Product List",
				{
					"product_name" : i.product_name,
					"quantity" : (">" , i.quantity)
				},
			)

			if not exists: frappe.throw(("You don't have enough product quantity to purchase the product"))


	def before_submit(self):

		self.submitted_date = date.today()

		sales_items = self.get("items")

		for i in sales_items:

			new_doc = frappe.get_doc({
				"doctype" : "Transaction Details",
				"party_type" : "Customer",
				"party_id" : self.customer_name,
				"company_name" : self.company_name,
				"product_name" : i.product_name,
				"quantity" : i.quantity,
				"rate" : i.rate,
				"amount" : i.amount,
				"date" : self.submitted_date,
				"ref_doctype" : "Sales Invoices",
				"out_quantity" : i.quantity,
				"invoice_id" : self.name
			})

			new_doc.insert(ignore_permissions=True)

			product = frappe.get_doc("Product List", i.product_name)

			if(product.quantity > i.quantity):
				product.quantity = product.quantity - i.quantity
				product.save(ignore_permissions=True)
			else:
				frappe.throw("You don't have sufficient quantity for sales")



