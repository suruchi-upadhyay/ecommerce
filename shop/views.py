from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, auth
from .models import Product, Contact, Order, OrderItem
from django.contrib import messages
from django.views.decorators.csrf import ensure_csrf_cookie
from math import ceil
import json
from django.views.decorators.csrf import csrf_exempt
# from PayTm import checksum
# Create your views here.
from django.http import HttpResponse

MERCHANT_KEY = 'Your-Merchant-Key-Here'


def index(request):
    allProds = []
    catprods = Product.objects.values('category', 'id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prod = Product.objects.filter(category=cat)
        n = len(prod)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        allProds.append([prod, range(1, nSlides), nSlides])
    params = {'allProds': allProds}
    return render(request, 'shop/index.html', params)


def searchMatch(query, item):
    '''return true only if query matches the item'''
    if query in item.desc.lower() or query in item.product_name.lower() or query in item.category.lower():
        return True
    else:
        return False


def search(request):
    query = request.GET.get('search')
    allProds = []
    catprods = Product.objects.values('category', 'id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prodtemp = Product.objects.filter(category=cat)
        prod = [item for item in prodtemp if searchMatch(query, item)]

        n = len(prod)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        if len(prod) != 0:
            allProds.append([prod, range(1, nSlides), nSlides])
    params = {'allProds': allProds, "msg": ""}
    if len(allProds) == 0 or len(query) < 4:
        params = {'msg': "Please make sure to enter relevant search query"}
    return render(request, 'shop/search.html', params)


def about(request):
    return render(request, 'shop/about.html')


def contact(request):
    thank = False
    if request.method == "POST":
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        phone = request.POST.get('phone', '')
        desc = request.POST.get('desc', '')
        contact = Contact(name=name, email=email, phone=phone, desc=desc)
        contact.save()
        thank = True
    return render(request, 'shop/contact.html', {'thank': thank})


def tracker(request):
    if request.method == "POST":
        orderId = request.POST.get('orderId', '')
        email = request.POST.get('email', '')
        try:
            order = Order.objects.filter(order_id=orderId, email=email)
            if len(order) > 0:
                update = OrderUpdate.objects.filter(order_id=orderId)
                updates = []
                for item in update:
                    updates.append({'text': item.update_desc, 'time': item.timestamp})
                    response = json.dumps({"status": "success", "updates": updates, "itemsJson": order[0].items_json},
                                          default=str)
                return HttpResponse(response)
            else:
                return HttpResponse('{"status":"noitem"}')
        except Exception as e:
            return HttpResponse('{"status":"error"}')

    return render(request, 'shop/tracker.html')


def productView(request, myid):
    # Fetch the product using the id
    product = Product.objects.filter(id=myid)
    return render(request, 'shop/prodView.html', {'product': product[0]})


def checkout(request):
    if request.method == "POST":
        items_json = request.POST.get('itemsJson', '')
        name = request.POST.get('name', '')
        amount = request.POST.get('amount', '')
        email = request.POST.get('email', '')
        address = request.POST.get('address1', '') + " " + request.POST.get('address2', '')
        city = request.POST.get('city', '')
        state = request.POST.get('state', '')
        zip_code = request.POST.get('zip_code', '')
        phone = request.POST.get('phone', '')
        order = Order(items_json=items_json, name=name, email=email, address=address, city=city,
                       state=state, zip_code=zip_code, phone=phone, amount=amount)
        order.save()
        update = OrderUpdate(order_id=order.order_id, update_desc="The order has been placed")
        update.save()
        thank = True
        id = order.order_id
        # return render(request, 'shop/checkout.html', {'thank':thank, 'id': id})
        # Request paytm to transfer the amount to your account after payment by user
        param_dict = {

            'MID': 'Your-Merchant-Id-Here',
            'ORDER_ID': str(order.order_id),
            'TXN_AMOUNT': str(amount),
            'CUST_ID': email,
            'INDUSTRY_TYPE_ID': 'Retail',
            'WEBSITE': 'WEBSTAGING',
            'CHANNEL_ID': 'WEB',
            'CALLBACK_URL': 'http://127.0.0.1:8000/shop/handlerequest/',

        }
        # param_dict['CHECKSUMHASH'] = checksum.generate_checksum(param_dict, MERCHANT_KEY)
        # return render(request, 'shop/paytm.html', {'param_dict': param_dict})

    return render(request, 'shop/checkout.html')



@ensure_csrf_cookie
def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            customer = get_object_or_404(Customer, email=email)
            print(customer)
            if customer.check_password(password):
                request.session['id'] = email
                request.session['type'] = 'customer'
                return redirect(index)
            else:
                messages.error(request, 'Password Incorrect')
                return redirect(index)
        except:

            try:
                vendor = get_object_or_404(Vendor, email=email)
                if vendor.check_password(password):
                    print(vendor.name)
                    if vendor.is_authorized:
                        print("Authorized")
                        request.session['id'] = email
                        request.session['type'] = ' vendor'
                        return redirect('/')
                    else:
                        messages.error(request, '  Vendor not Approved')
                        return redirect('/')
                else:
                    messages.error(request, 'Password Incorrect')
                    return redirect('/')
            except Exception as e:
                messages.error(request, 'No Customer or Vendor is registered with this email')
                print(e)
                return redirect('/')
    else:
        return render(request, "shop/login.html")

def logout(request):
    try:
        del request.session['id']
        del request.session['type']
        request.session.modified = True
    except KeyError:
        pass
    return render(request, 'shop/login.html')


def signup(request):
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        username = request.POST['username']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        usertype = request.POST.get('usertype')
        if usertype == 'customer':
            user = Customer(name=name, email=email)
            user.set_password(user.make_password(password2))
            user.save()
            request.session['id'] = email
            request.session['type'] = 'customer'
        elif usertype == 'vendor':
            user = Vendor(name=name, email=email, is_authorized=False)
            user.set_password(user.make_password(password2))
            user.save()
            request.session['id'] = email
            request.session['type'] = 'vendor'
            messages.error(request, 'Vendor not Approved')
        return render(request, "shop/signup.html")

    else:
        return render(request, "shop/signup.html")

@csrf_exempt
def handlerequest(request):
    # paytm will send you post request here
    form = request.POST
    response_dict = {}
    for i in form.keys():
        response_dict[i] = form[i]
        if i == 'CHECKSUMHASH':
            checksum = form[i]

    # verify = Checksum.verify_checksum(response_dict, MERCHANT_KEY, checksum)
    # if verify:
    #     if response_dict['RESPCODE'] == '01':
    #         print('order successful')
    #     else:
    #         print('order was not successful because' + response_dict['RESPMSG'])
    return render(request, 'shop/paymentstatus.html', {'response': response_dict})

def vendor(request):
    vendor = Vendor.objects.get(email=request.session['id'])
    product_name = Product.objects.all()
    menu = {}
    for fi in product_name:
        if fi.resid == vendor:
            try:
                menu[fi.cuisine].append(fi)
            except KeyError:
                menu[fi.cuisine] = [fi]
        context = {
            'product': restaurant,
            'menu': menu
        }
    return render(request, 'foodspark/restprofile.html', context)