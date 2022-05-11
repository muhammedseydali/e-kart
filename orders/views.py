from django.shortcuts import redirect, render
from carts.models import Cart,CartItem
# Create your views here.
def place_order(request):
    current_user = request.user

    # if the cart count is less than or equal to 0, then redirect back to shop
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <=0:
        return redirect('store')
    return render(request,'place_order.html')
