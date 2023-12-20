# Copyright (c) 2023, Sudharsanan Ashok and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class StockAvailability(Document):
	def befor_save(self):

		exists = frappe.db.exists(
			"Stock Availability",
			{
				"product": self.product,
				"location": self.location,
			}
		)	
		if exists:
			stock_availability = frappe.get_doc("Stock Availability", self.product, self.location)
			stock_availability.quantity = stock_availability.quantity + self.quantity
			stock_availability.save()
		else:
			frappe.throw("")

	