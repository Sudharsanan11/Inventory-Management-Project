import frappe 

@frappe.whitelist()
# def create_document(data):
#     transaction_details = frappe.new_doc("Transaction Details")

#     transaction_details.supplier = data.supplier
#     transaction_details.product_name = data.productName
#     transaction_details.quantity = data.quantity
#     transaction_details.rate = data.rate
#     transaction_details.amount = data.amount

#     transaction_details.insert(ignore_permissions=True)

#     return transaction_details.name
@frappe.whitelist()
def get_value(product_name):
    return frappe.get_value("Product List", product_name, "base_amt")

@frappe.whitelist()
def get_mrp(product_name):
    return frappe.get_value("Product List", product_name, "act_amt")