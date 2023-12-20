# Copyright (c) 2023, Sudharsanan Ashok and contributors
# For license information, please see license.txt

import frappe
from frappe import _

field_map = {
	# "Stock Availability": [
	# 	"product",
	# 	"location",
	# 	"quantity",
	# ],
	"Stock Movement": [
		"product",
		"from_location",
		"to_location",
		"stock_quantity",
		"status",
		"date",
		"time",
	]
}

def execute(filters=None):
	columns, data = get_columns(filters), get_data(filters)
	return columns, data


def get_columns(filters):
	return [
		"{reference_doctype}:Link/{reference_doctype}".format(
			reference_doctype=filters.get("reference_doctype")
		),
		# "product",
		# "location",
		# "quantity",
		"product",
		"from_location",
		"to_location",
		"stock_quantity",
		"status",
		"date",
		"time",
	]

def get_data(filters):
	data = []
	reference_doctype = filters.get("reference_doctype")
	reference_name = filters.get("reference_name")

	return get_reference_stock_availability_and_stock_movement(reference_doctype, reference_name)

def get_reference_stock_availability_and_stock_movement(reference_doctype, reference_name):
	data = []
	filters = None
	reference_details = frappe._dict()

	if not reference_doctype:
		return []

	if reference_name:
		filters = {"name": reference_name}

	reference_list = frappe.get_list(reference_doctype, filters=filters, fields=["name","product","from_location","to_location","stock_quantity","status","date","time"],as_list=True)
	print(reference_list)
	result =[]
	for data in reference_list:
		data = [" "]+list(data)
		for i in range(len(data)):
			if not data[i]:
				data[i] = ""
		result.append(data)

	# for d in reference_list:
	# 	reference_details.setdefault(d, frappe._dict())

	# # reference_details = get_reference_details(
	# # 	reference_doctype, "Stock Availability", reference_list, reference_details
	# # )

	# reference_details = get_reference_details(
	# 	reference_doctype, "Stock Movement", reference_list, reference_details
	# )
	# print(reference_details)

	# for reference_name, details in reference_details.items():
	# 	# stock_availability = details.get("location", [])
	# 	stock_movement = details.get("product", [])
	# 	if not any(stock_movement):
	# 		result = [reference_name]
	# 		# result.extend(add_blank_columns_for("Stock Availability"))
	# 		result.extend(add_blank_columns_for("Stock Movement"))
	# 		data.append(result)
	# 	else:
	# 		# stock_availability = list(map(list, stock_availability))
	# 		stock_movement = list(map(list, stock_movement))

	# 		# max_length = max(len(stock_availability), len(stock_movement))
	# 		for idx in range(0, len(stock_movement)):
	# 			result = [referenece_name]

	# 			# result.extend(stock_availability[idx] if idx < len(stock_availability) else add_blank_columns_for("Stock Availability"))
	# 			result.extend(stock_movement[idx] if idx <len(stock_movement) else add_blank_columns_for("Stock Movement"))

	# 			data.append(result)
	print(result)	
	return result

# def get_reference_details(reference_doctype,doctype,reference_list,reference_details):
# 	filters = [
# 		["Dynamic Link", "link_doctype", "=", reference_doctype],
# 		["Dynamic Link", "link_name", "in", reference_list],
# 	]
# 	fields = ["`tabDynamic Link`.link_name"] + field_map.get(doctype, [])

# 	records = frappe.get_list(doctype, filters=filters, fields=fields, as_list=True)
# 	temp_records = list()

# 	for d in records:
# 		temp_records.append(d[1:])

# 	if not reference_list:
# 		frappe.throw(_("No records present in {0}").format(reference_doctype))

# 	reference_details[reference_list[0]][frappe.scrub(doctype)] = temp_records
# 	#print(reference_details)
# 	return reference_details

def add_blank_columns_for(doctype):
	return ["" for field in field_map.get(doctype, [])]