
from email.message import EmailMessage
from django import urls
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.contrib import messages,auth
from .models import Account
from carts.models import Cart,CartItem
from carts.views import _cart_id
from .forms import RegistrationForm
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.http import request

# Create your views here.

@login_required(login_url='login')
def user_dashboard(request):
    user=Account.objects.get(email=request.user)
    order_count=Order.objects.filter(user=request.user).count()
    
    cancelled_order_count=Order.objects.filter(user=request.user,status='Cancelled').count()
    import decimal

    decimal.getcontext().prec = 2

    
    try:
        customer_rating=decimal.Decimal(order_count-cancelled_order_count)/decimal.Decimal(order_count)
    except:
        customer_rating=1
    customer_rating_percent = customer_rating*100
    customer_rating=customer_rating*5
    
    context={
        'user': user,
        'order_count':order_count,
        'cancelled_order_count':cancelled_order_count,
        'customer_rating':customer_rating,
        'customer_rating_percent':customer_rating_percent,
    }
    return render(request, 'user_dashboard.html',context)
    
def register(request):
    if request.method == 'POST':
        forms = RegistrationForm(request.POST)
        if forms.is_valid():
            first_name = forms.cleaned_data['first_name']
            last_name = forms.cleaned_data['last_name']
            phone_number = forms.cleaned_data['phone_number']
            email = forms.cleaned_data['email']
            password = forms.cleaned_data['password']
            user_name = email.split('@')[0]
           
            user = Account.objects.create_user(first_name=first_name, last_name=last_name, email=email, username=user_name, password=password )
            user.phone_number = phone_number
            user.save()

            # user registration
            current_site = get_current_site(request)
            mail_subject = 'please activate your account'
            message = render_to_string ('accounts/account_verification_email.html',{
                'user':user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token':default_token_generator.make_token(user),
            })  
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()
            messages.success(request, 'Registartion successful')
            return redirect('/accounts/login/?command=verification&email='+email)
    else:
        forms = RegistrationForm()    
    context = {
        'forms':forms,
    }
    return render(request, 'accounts/register.html',context)



def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(email=email, password=password)

        if user is not None:
            try:
                cart = Cart.objects.get(cart_id = _cart_id(request))
                is_cart_item_exists = CartItem.objects.filter(cart=cart).exists()
                if is_cart_item_exists:
                    cart_item = CartItem.objects.filter(cart=cart)

                    for item in cart_item:
                        item.user = user
                        item.save()
            except:
                pass    
            auth.login(request,user)
            messages.success(request,'you are now logged in')
            url = request.META.get('HTTP_REFER')
            try:
                query = request.utils.urlparse(url).query
                params = dict(x.split('=')for x in query.split('&'))
                if 'next' in params:
                    nextPage = params['next']
                    return redirect(nextPage)
            except:
                return redirect('dashboard')
        else:
            messages.error(request, 'invalid login credentials')
            return redirect('login')    
    return render(request, 'accounts/login.html')

@login_required(login_url = 'login')
def logout(request):
    auth.logout(request)
    messages.success(request,'You are logged out!!!')
    return redirect('login')

def activate(request,uidb64,token ):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError,OverflowError,Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user,token):
        user.is_active = True
        user.save()
        messages.success(request, "Congargulations your account is activated")
        return redirect('login')

    else:
        messages.error(request, 'Invalid activation link')
        return redirect('register')   


@login_required(login_url='login')
def dashboard(request):
    return render(request,'accounts/dashboard.html')

def forgetPassword(request):
    if request.method == 'POST':
        email = request.POST['email']
        if Account.objects.filter(email=email).exists():
            user =Account.objects.get(email__exact=email)


        # reset password mail
        current_site = get_current_site(request)
        mail_subject = 'Reset your pasword'
        message = render_to_string('accounts/reset_password_email.html',{
            'user' : user,
            'domain': current_site,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token':default_token_generator.mute_token(user),
        }) 

        to_email = email
        send_email = EmailMessage(mail_subject,message, to=[to_email])
        send_email.send()

        messages.success(request, "password email has sent to your email address")
        return redirect('login')
    return render(request,'accounts/forgetpassword.html')    


def resetpassword_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uid).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None


    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, 'please reset your password')
        return redirect('resetPassword')

    return HttpResponse('ok')
    
def resetPassword(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']    

        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request,'password reset successful')
            return redirect('login')

        else:
            messages.error(request, 'Paasword do not match')
            return redirect('resetPassword')
    else:
        return render(request, 'accounts/resetPassword.html' )        
