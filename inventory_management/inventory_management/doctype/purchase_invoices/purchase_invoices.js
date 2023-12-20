// Copyright (c) 2023, Sudharsanan Ashok and contributors
// For license information, please see license.txt

frappe.ui.form.on('Purchase Invoices', {
	// refresh: function(frm) {

	// }
	// onsubmit: function(frm,cdt,cdn){
	// 	let row = locals[cdt][cdn]
	// 	var data = {
	// 		supplier : frm.supplier,
	// 		productName : row.product_name,
	// 		quantity : row.quantity,
	// 		rate : row.rate,
	// 		amount : row.amount
	// 	};
	// 	frappe.call({
	// 		methode: "inventory_management.inventory_management.create_document",
	// 		args : {
	// 			data : data
	// 		},
	// 		callback : function(response){
	// 			if(response.message){
	// 				frappe.msgprint(__("Document Created {0}",[response.message]));
	// 			}
	// 		} 
	// 	})
	// }
});
frappe.ui.form.on('Purchase Items', {
	product_name:function(frm,cdt,cdn){
		let row = locals[cdt][cdn]
		
		// base_amt = frappe.get_value("Product List", {'prname':row.product_name}, "base_amt")
		// row.rate = base_amt
		// frm.refresh_fields()

		frappe.call({
			method : "inventory_management.methods.get_value",
			args : {
				product_name : row.product_name
			},
			callback : function(response){
				var rate = response.message
				row.rate = rate
				frm.refresh_fields()
			}
		})
	},
	quantity:function(frm,cdt,cdn){
		let row = locals[cdt][cdn]
		let quantity = row.quantity
		let amount = row.amount
		let rate = row.rate
		amount = quantity * rate
		row.amount = amount
		frm.refresh_fields()
	},
	rate:function(frm,cdt,cdn){
		let row = locals[cdt][cdn]
		let quantity = row.quantity
		let rate = row.rate

		row.amount = rate * quantity
		frm.refresh_fields()
	}

})