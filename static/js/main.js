$('.cart-add-product-form button').on('click', function (ev) {
    ev.preventDefault()
    var xhr = $.post(
	'/user/cart/add',
	$(ev.target.parentElement).serialize())

    xhr.done(function (data) {
	toastr.success('Επιτυχής πρσθήκη προιόντος')
    })
})
