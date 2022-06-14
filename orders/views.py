from datetime import datetime
from django.shortcuts import redirect, render
from carts.models import Cart,CartItem
from .models import Order
from .forms import OrderForm
# Create your views here.
def place_order(request, total=0,quantity = 0):
    current_user = request.user

    # if the cart count is less than or equal to 0, then redirect back to shop
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <=0:
        return redirect('store')

    grand_total = 0
    tax = 0
    for cart_items in cart_items:
        total += (cart_items.product.price * cart_items.quantity)
        quantity += cart_items.quantity

    tax = (2 * total)/100
    grand_total = total + tax    

    if request.method == 'POST':
        form = OrderForm(request.POST)
        # store all the billing informations inside order table

        data = Order() 
        data.user = current_user
        data.first_name = form.cleaned_data('first_name')
        data.last_name = form.cleaned_data('last_name')
        data.phone = form.cleaned_data('phone')
        data.email = form.cleaned_data('email')
        data.address_line = form.cleaned_data('address_line')
        data.address_line2 = form.cleaned_data('address_line2')
        data.country = form.cleaned_data('country')
        data.city = form.cleaned_data('city')
        data.order_note = form.cleaned_data('order_note')
        data.order_total = form.cleaned_data('order_total')
        data.tax = form.cleaned_data('tax')
        data.ip = request.META.get('REMOTE_ADDR')
        data.save()
        return redirect('checkout')

        # generate order number
        yr = int(datetime.date.today().strftime('%Y'))
        dt = int(datetime.date.today().strftime('%d'))
        mt = int(datetime.date.today().strftime('%m'))
        d = datetime.date.strftime('%Y')
        current_date = d.strftime("%Y%m%d")
        order_number = current_date + str(data.id)
        data.order_number = order_number
        data.save()

        order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
        context= {
            'order':order,
            'cart_items':cart_items,
            'total':total,
            'tax':tax,
            'grand_total':grand_total
        }
        return render(request,'payments.html',context)
    else:
        return render(request,'place_order.html')


def payments(request):
    return render(request, 'payments.html')