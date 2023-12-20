// Copyright (c) 2023, Sudharsanan Ashok and contributors
// For license information, please see license.txt

frappe.ui.form.on('Sales Invoices', {
	// refresh: function(frm) {

	// }
});

frappe.ui.form.on("Purchase Items", {
	product_name:function(frm,cdt,cdn){
		let item = locals[cdt][cdn]

		frappe.call({
			method : "inventory_management.methods.get_mrp",
			args : {
				product_name : item.product_name
			},
			callback : function(response){
				var mrp = response.message
				item.rate = mrp
				frm.refresh_fields()
			}
		})
	},
	quantity:function(frm,cdt,cdn){
		let item = locals[cdt][cdn]
		let quantity = item.quantity
		let rate = item.rate

		item.amount = quantity * rate
		frm.refresh_fields()
	}
})
