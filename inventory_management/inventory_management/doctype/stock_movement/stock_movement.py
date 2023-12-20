# Copyright (c) 2023, Sudharsanan Ashok and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.docstatus import DocStatus
from datetime import date

class StockMovement(Document):
	def before_save(self):
		if(self.from_location != self.to_location):
			if(self.status == "Departed"):
				self.validate_from_location()
				self.validate_quantity()

			elif(self.status == "Delivered"):
				self.validate_availability()
		else:
			frappe.throw("From Location can not be same as To Location")

	def validate_from_location(self):
		exists = frappe.db.exists(
			"Stock Availability",
			{
				"location": self.from_location,
				"product": self.product
			}
		)

		if not exists:
			frappe.throw("The Product that you are entered does not exists in a specified location")

	def validate_quantity(self):
		check_availability = self.from_location + "-" + self.product
		# frappe.throw(type(check_availability))
		location = frappe.get_doc("Stock Availability", {"name":check_availability})
		# frappe.msgprint(location)

		if(int(location.quantity) < self.stock_quantity):
			frappe.msgprint("if block working")
			frappe.throw("Invalid Quantity")

	def validate_availability(self):

		exists = frappe.db.exists(
			"Stock Movement",
			{
				"from_location": self.from_location,
				"to_location": self.to_location,
				"docstatus": DocStatus.submitted(),
				"stock_quantity": self.stock_quantity
			}
		)
		if not exists:
			frappe.throw("The data does not exists")
	
	def before_submit(self):
		self.date = date.today()

	def on_submit(self):
		self.change_quantity()

	def change_quantity(self):
		if(self.status == "Departed"):
			check_availability = self.from_location + "-" + self.product
			check_quantity = frappe.get_doc("Stock Availability" , {"name":check_availability})
			check_quantity.quantity = int(check_quantity.quantity) - self.stock_quantity
			check_quantity.save()
		elif(self.status == "Delivered"):
			self.validate_stock()


	def validate_stock(self):
		exists = frappe.db.exists(
			"Stock Availability",
			{
				"location": self.to_location,
				"product": self.product
			}
		)
		if exists:
			check_availability = self.to_location + "-" + self.product
			check_quantity = frappe.get_doc("Stock Availability", {"name":check_availability})
			check_quantity.quantity = int(check_quantity.quantity) + self.stock_quantity
			check_quantity.save()
		else:
			self.add_new_doc()
	
	def add_new_doc(self):

		new_doc = frappe.get_doc(
			{
				"doctype": "Stock Availability",
				"location": self.to_location,
				"product": self.product,
				"quantity": self.stock_quantity
			}
		)
		new_doc.insert()
		frappe.msgprint(f"New Product has inserted into {self.to_location} inventory")