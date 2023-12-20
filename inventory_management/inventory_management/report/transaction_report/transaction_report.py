# Copyright (c) 2023, Sudharsanan Ashok and contributors
# For license information, please see license.txt
import functools
import math
import re
import frappe
from frappe import _
from frappe.utils import add_days, add_months, cint, cstr, flt, formatdate, get_first_day, getdate
from erpnext.accounts.utils import get_fiscal_year
import datetime
from datetime import date
import dateutil.relativedelta as relativedelta

def execute(filters):
	print(filters)
	columns, data = get_columns(filters) , get_data(filters)

	company = filters.get("company_name")
	filter_based_on = filters.get("filter_based_on")
	period_start_date = filters.get("period_start_date")
	period_end_date = filters.get("period_end_date")
	from_fiscal_year = filters.get("from_fiscal_year")
	to_fiscal_year = filters.get("to_fiscal_year")
	periodicity = filters.get("periodicity")
	party_type = filters.get("party_type")
	party_id = filters.get("party_id")
	product_name = filters.get("product_name")
	invoice_doctype = filters.get("invoice_doctype")
	invoice_id = filters.get("invoice_id")

	year_start_date, year_end_date = None, None

	if filter_based_on == "Fiscal Year":
		fiscal_year = get_fiscal_year_data(from_fiscal_year, to_fiscal_year)
		validate_fiscal_year(fiscal_year, from_fiscal_year, to_fiscal_year)
		year_start_date = getdate(fiscal_year.year_start_date)
		year_end_date = getdate(fiscal_year.year_end_date)
		
	elif filter_based_on == "Date Range":
		validate_dates(period_start_date, period_end_date)
		year_start_date = getdate(period_start_date)
		year_end_date = getdate(period_end_date)

	expence = """SELECT SUM(amount) AS amount 
				FROM `tabTransaction Details`
				WHERE company_name='{company}' 
				AND party_type='Supplier' 
				AND date BETWEEN '{year_start_date}' 
				AND '{year_end_date}'""".format(company= company, year_start_date= year_start_date, year_end_date= year_end_date)
	income = """SELECT SUM(amount) AS amount 
				FROM `tabTransaction Details` 
				WHERE company_name='{company}' 
				AND party_type='Customer' 
				AND date BETWEEN '{year_start_date}'
				AND '{year_end_date}'""".format(company=company, year_start_date= year_start_date, year_end_date= year_end_date)

	if product_name:
		expence += " AND product_name='{product_name}'".format(product_name=product_name)
		income += " AND product_name='{product_name}'".format(product_name=product_name)
	
	query = frappe.db.sql(expence, as_dict=1)
	query2 = frappe.db.sql(income, as_dict=1)
	expence	= query[0].amount
	income = query2[0].amount
	net_profit_loss = get_net_profit_loss(filters,income,expence)
	
	report_summary = get_report_summary(income,expence,net_profit_loss)

	chart = get_chart_data(filters,income,expence,net_profit_loss,year_start_date,year_end_date,periodicity)

	return columns, data, None, chart, report_summary 


def get_chart_data(filters,income,expence,net_profit_loss,year_start_date,year_end_date,periodicity):

	company = filters.get("company_name")
	product_name = filters.get("product_name")
	months_to_add = {"Monthly" : 1, "Quarterly" : 3, "Half-Yearly" : 2, "Yearly" : 12}[periodicity]

	months = get_months(year_start_date, year_end_date)
	start_date = year_start_date
	income_list, expence_list, profit_list = [], [], []
	monthly_expance, monthly_income, monthly_profit = 0.0, 0.0, 0.0
	
	for i in range(int(math.ceil(months / months_to_add))):
		month_end_date = add_months(start_date, +1)
		end_date = add_days(month_end_date, -1)

		month_expence = """SELECT 
								SUM(amount) AS amount 
							FROM `tabTransaction Details` 
							WHERE company_name='{company}' 
								AND party_type='Supplier' 
								AND date BETWEEN '{start_date}' 
								AND '{end_date}'""".format(company= company, start_date= start_date, end_date= end_date)
		month_income = f"""SELECT SUM(amount) AS amount 
						FROM `tabTransaction Details` 
						WHERE company_name='{company}' 
							AND party_type='Customer' 
							AND date BETWEEN '{start_date}'
							AND '{end_date}'""".format(company= company, start_date= start_date, end_date= end_date)
		
		if product_name:
			month_expence += " AND product_name='{product_name}'".format(product_name=product_name)
			month_income += " AND product_name='{product_name}'".format(product_name=product_name)

		query = frappe.db.sql(month_expence,as_dict=1, debug=True)
		query2 = frappe.db.sql(month_income, as_dict=1)
		if query[0].amount == None:
			query[0].amount = 0.0
		if query2[0].amount == None:
			query2[0].amount = 0.0
	
		monthly_expence = query[0].amount
		monthly_income = query2[0].amount
		income_list.append(monthly_income)
		expence_list.append(monthly_expence)

		filter = {}
		
		filter['date'] = ("between",[start_date, end_date])
		if product_name:
			filter['product_name'] = product_name
		filter['party_type'] = "Customer"

		product = frappe.get_list("Transaction Details", filters=filter, fields=["product_name","out_quantity"])
		net_income, net_expense, monthly_profit_loss = 0.0, 0.0, 0.0
		for i in range(len(product)):
			product_list = frappe.get_list("Product List", filters= {"name" : product[i].product_name}, fields=['base_amt','act_amt'])
			net_expense += product[i].out_quantity * product_list[0].base_amt
			net_income += product[i].out_quantity * product_list[0].act_amt

			monthly_profit_loss = net_income - net_expense

		profit_list.append(monthly_profit_loss)
		start_date = month_end_date


	label = []
	income_data, expence_data, net_profit = [], [], []

	for period in range(int(math.ceil(months / months_to_add))):
		year_end_date = add_months(year_start_date, +1)
		if periodicity == "Monthly" or periodicity == "Quarterly" or periodicity == "Half-Yearly":
			label.append(formatdate(year_start_date, "MMM YYYY"))
			year_start_date = year_end_date

	if periodicity == "Yearly":
		label.append(formatdate(year_start_date, "YYYY") + "-" + formatdate(year_end_date, "YYYY"))
		income_list, expence_list, profit_list = [], [], []
		income_list.append(income)
		expence_list.append(expence)
		profit_list.append(net_profit_loss)
	else:
		label.append('Total')
		income_list.append(sum(income_list))
		expence_list.append(sum(expence_list))
		profit_list.append(sum(profit_list))

	datasets = []

	if income:
		datasets.append({"name" : _("Income"), "values" : income_list})
	if expence:
		datasets.append({"name" : _("Expence"), "values" : expence_list})
	if net_profit_loss:
		datasets.append({"name" : _("Net Profit/Loss"), "values" : profit_list})

	chart = {"data" : {"labels" : label, "datasets" : datasets}}
	chart["type"] = "bar" 
	chart["fieldtype"] = "Currency"
		
	return chart

def get_columns(filters):
	columns = [
		{
			"label" : _("Transaction ID"),
			"fieldtype" : "Link",
			"fieldname" : "name",
			"options" : "Transaction Details",
		},
		{
			"label" : _("Party Type"),
			"fieldtype" : "Select",
			"fieldname" : "party_type",
			"options" : ["Supplier","Customer"],
		},
		{
			"label" : _("Party ID"),
			"fieldtype" : "Dynamic Link",
			"fieldname" : "party_id",
			"options" : "party_type",
		},
		{
			"label" : _("Company Name"),
			"fieldtype" : "Link",
			"fieldname" : "company_name",
			"options" : "Company",
		},
		{
			"label" : _("Product Name"),
			"fieldtype" : "Link",
			"fieldname" : "product_name",
			"options" : "Product List",
		},
		{
			"label" : _("Quantity"),
			"fieldtype" : "Float",
			"fieldname" : "quantity",
		},
		{
			"label" : _("Rate"),
			"fieldtype" : "Currency",
			"fieldname" : "rate",
		},
		{
			"label" : _("Amount"),
			"fieldtype" : "Currency",
			"fieldname" : "amount",
		},
		{
			"label" : _("Date"),
			"fieldtype" : "Date",
			"fieldname" : "date",
		},
		{
			"label" : _("Reference DocType"),
			"fieldtype" : "Select",
			"fieldname" : "ref_doctype",
			"options" : ["Purchase Invoices","Sales Invoices"],
		},
		{
			"label" : _("Invoice ID"),
			"fieldtype" : "Dynamic Link",
			"fieldname" : "invoice_id",
			"options" : "ref_doctype",
		},
		{
			"label" : _("In Quantity"),
			"fieldtype" : "Float",
			"fieldname" : "in_quantity",
		},
		{
			"label" : _("Out Quantity"),
			"fieldtype" : "Float",
			"fieldname" : "out_quantity",
		},
	]

	return columns

def get_fiscal_year_data(from_fiscal_year, to_fiscal_year):
	fiscal_year = frappe.db.sql(
		"""select min(year_start_date) as year_start_date,
		max(year_end_date) as year_end_date from `tabFiscal Year` where
		name between %(from_fiscal_year)s and %(to_fiscal_year)s""",
		{"from_fiscal_year": from_fiscal_year, "to_fiscal_year": to_fiscal_year},
		as_dict=1,
	)

	return fiscal_year[0] if fiscal_year else {}

def validate_fiscal_year(fiscal_year, from_fiscal_year, to_fiscal_year):
	if not fiscal_year.get("year_start_date") and not fiscal_year.get("year_end_date"):
		frappe.throw(_("Start Year and End Year are Mandatory"))
	if to_fiscal_year < from_fiscal_year:
		frappe.throw(_("End Year cannot be before Start Year"))

def validate_dates(from_date, to_date):
	if not from_date and not to_date:
		frappe.throw("From Date and To Date are Mandatory")
	if to_date < from_date:
		frappe.throw("To Date cannot be less than then From Date")

def get_net_profit_loss(filters,income,expence):
	company = filters.get("company_name")
	from_date = filters.get("from_date")
	to_date = filters.get("to_date")
	product_name = filters.get("product_name")
	filter = {}

	if company:
		filter = {"company_name" : company}
	if from_date and to_date:
		filter['date'] = ("between",[from_date, to_date])
	if product_name:
		filter['product_name'] = product_name
	filter['party_type'] = "Customer"

	product = frappe.get_list("Transaction Details", filters=filter, fields=["product_name","out_quantity"])
	net_income, net_expense, net_profit = 0.0, 0.0, 0.0
	print(product)
	for i in range(len(product)):
		product_list = frappe.get_list("Product List", filters= {"name" : product[i].product_name}, fields=['base_amt','act_amt'])
		net_expense += product[i].out_quantity * product_list[0].base_amt
		net_income += product[i].out_quantity * product_list[0].act_amt

		net_profit_loss = net_income - net_expense

	return net_profit_loss

def get_report_summary(income,expence,net_profit_loss):

	return[
		{'value' : income, 'label': "Total Income", 'datatype' : "Currency"},
		{'type' : "Separator",'label' : "", 'value' : "-"},
		{'value' : expence, 'label' : "Total Expence", 'datatype' : "Currency"},
		{'type' : "Separator",'label' : "", 'value' : "=", 'color' : "blue",},
		{
			'value' : net_profit_loss,
			'label' : "Total Profit/Loss",
			'indicator' : "Green" if net_profit_loss > 0 else "Red",
			'datatype' : "Currency",
		},
	]

def get_data(filters):
	data = []
	filter = {}

	company = filters.get("company_name")
	from_date = filters.get("from_date")
	to_date = filters.get("to_date")
	party_type = filters.get("party_type")
	party_id = filters.get("party_id")
	product_name = filters.get("product_name")
	invoice_doctype = filters.get("invoice_doctype")
	invoice_id = filters.get("invoice_id")
	in_quantity = filters.get("in_quantity")
	out_quantity = filters.get("out_quantity")

	if company:
		filter = {"company_name" : company}
	if from_date and to_date:
		filter['date'] = ("between",[from_date, to_date])
	if party_type:
		filter['party_type'] = party_type
	if party_id:
		filter['party_id'] = party_id
	if product_name:
		filter['product_name'] = product_name
	if invoice_doctype:
		filter['ref_doctype'] = invoice_doctype
	if invoice_id:
		filter['invoice_id'] = invoice_id


	reference_list = frappe.get_list("Transaction Details", filters=filter, fields=["name", "party_type", "party_id", "company_name", "product_name", "quantity", "rate", "amount", "date", "ref_doctype", "invoice_id", "in_quantity", "out_quantity"],order_by="date")
	result = []

	# for i in reference_list:
	# 	data = list(i)
	# 	result.append(data)
	print(reference_list,"\n\n\n\n\n\n\n\n\n")
	return reference_list
def get_months(start_date, end_date):
	diff = (12 * end_date.year + end_date.month) - (12 * start_date.year + start_date.month)
	return diff + 1


	
