from .models import Cart

def cart_processores(request):
	cart_item = 0
	cart_obj = None
	if request.user.is_authenticated:
		try:
			cart_obj = Cart.objects.get(
				user=request.user,
				status="pending")
			cart_item = cart_obj.cartproduct_set.count()
			request.session['cart_id'] = cart_obj.id
			get_cart_session_id = cart_obj.id
		except Exception as e:
			try:
				get_cart_session_id = request.session['cart_id']
			except Exception as e:
				get_cart_session_id = None

			if get_cart_session_id:
				try:
					cart_obj = Cart.objects.get(id=get_cart_session_id)
					cart_obj.user = request.user
					cart_obj.save()
					cart_item = cart_obj.cartproduct_set.count()
				except Exception as e:
					del request.session['cart_id']

	else:
		try:
			get_cart_session_id = request.session['cart_id']
		except Exception as e:
			get_cart_session_id = None

		if get_cart_session_id:
			try:
				cart_obj = Cart.objects.get(id=get_cart_session_id)
				cart_item = cart_obj.cartproduct_set.count()
			except Exception as e:
				del request.session['cart_id']

	return {
		'cart_session_id':get_cart_session_id,
		'cart_item':cart_item,
		'global_cart_obj':cart_obj,
	}