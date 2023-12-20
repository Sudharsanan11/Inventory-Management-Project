# Copyright (c) 2023, Sudharsanan Ashok and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import date

class PurchaseInvoices(Document):
	def before_submit(self):
		
		purchase_items = frappe.get_all("Purchase Items", filters={"parenttype" : "Purchase Invoices", "parent" : self.name}, fields=["product_name","quantity","rate","amount"])
		purchase_items = self.get("items")
		print("============================================================")
		print(purchase_items)
		print("============================================================")

		today = date.today()
		# formatted_date = today.strftime("DD-MM-YYYY")
		self.submitted_date = today

		for items in purchase_items:
			# new_doc = frappe.new_doc({
			# 	"doctype" : "Transaction Details",
			# 	"supplier" : self.supplier,
			# 	"date" : self.date,
			# 	"product_name" : items.product_name,
			# 	"quantity" : items.quantity,
			# 	"rate" : items.rate,
			# 	"amount" : items.amount
			# })
			new_doc = frappe.new_doc("Transaction Details")
			new_doc.part_type = "Supplier"
			new_doc.party_id =  self.supplier
			new_doc.company_name = self.company_name
			new_doc.date = self.submitted_date
			new_doc.product_name = items.product_name
			new_doc.quantity = items.quantity
			new_doc.in_quantity = items.quantity
			new_doc.rate = items.rate
			new_doc.amount = items.amount
			new_doc.ref_type = "Purchase Invoices"
			new_doc.invoice_id = self.name
			
			new_doc.save(ignore_permissions=True)

			product = frappe.get_doc("Product List", items.product_name)

			product.quantity = product.quantity + items.quantity
			product.save()