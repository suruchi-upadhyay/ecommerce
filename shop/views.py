from shop.forms import UserForm
from django.views import generic
from django.urls import reverse_lazy
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, auth
from .models import Product, Contact, Category, Product, Order, OrderItem
from django.contrib import messages
from django.views.decorators.csrf import ensure_csrf_cookie
from math import ceil
import json
from django.views.decorators.csrf import csrf_exempt
# from PayTm import checksum
# Create your views here.
from django.http import HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

MERCHANT_KEY = 'Your-Merchant-Key-Here'


# class SignUp(generic.CreateView):
#     form_class = UserForm
#     success_url = reverse_lazy('login')
#     template_name = 'shop/signup.html'


def index(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)

        products = products.filter(category=category)
    page = request.GET.get('page')
    paginator = Paginator(products, 6)
    try:
        products = paginator.page(page)

    except PageNotAnInteger:
        products = paginator.page(1)

    except EmptyPage:
        products = paginator.page(1)

    if request.user:
        print(request.user)
        pass
        # wishlist = Wishlist.objects.filter(user=request.user)

        return render(
            request,
            'shop/index.html',
            {
                'category': category,
                'categories': categories,
                'products': products,
                # 'wishlist': wishlist
            }
        )

    else:
        return render(
            request,
            'shop/index.html',
            {
                'category': category,
                'categories': categories,
                'products': products,
            }
        )


def searchMatch(query, item):
    '''return true only if query matches the item'''
    if query in item.description.lower() or query in item.name.lower():
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
    params = {
        'products': allProds,
        "msg": ""
    }
    if len(allProds) == 0 or len(query) < 4:
        params = {
            'msg': "Please make sure to enter relevant search query"
        }
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
                    updates.append(
                        {
                            'text': item.update_desc,
                            'time': item.timestamp
                        }
                    )
                    response = json.dumps(
                        {
                            "status": "success",
                            "updates": updates,
                            "itemsJson": order[0].items_json
                        },
                        default=str
                    )
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
        address = request.POST.get('address1', '') + \
            " " + request.POST.get('address2', '')
        city = request.POST.get('city', '')
        state = request.POST.get('state', '')
        zip_code = request.POST.get('zip_code', '')
        phone = request.POST.get('phone', '')
        order = Order(
            items_json=items_json,
            name=name, email=email,
            address=address, city=city,
            state=state,
            zip_code=zip_code,
            phone=phone,
            amount=amount
        )
        order.save()
        update = OrderUpdate(
            order_id=order.order_id,
            update_desc="The order has been placed"
        )
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
            'CALLBACK_URL': 'http://127.0.0.1:8000/handlerequest/',

        }
        # param_dict['CHECKSUMHASH'] = checksum.generate_checksum(param_dict, MERCHANT_KEY)
        # return render(request, 'shop/paytm.html', {'param_dict': param_dict})

    return render(request, 'shop/checkout.html')


def signup(request):

    
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
                user = form.save(commit=False)
                # commit=False tells Django that "Don't send this to database yet.
                    # I have more things I want to do with it."
                
                # import pdb;pdb.set_trace()
                if form.cleaned_data['type']=='Vendor':
                    
                    user.is_staff = True  # Set the user object here    
                    user.save()
                    return redirect("/admin/login") 
                else:
                    user.is_staff = False  
                    user.save()
                    return redirect("/login")  # Now you can send it to DB

                

                
        else:
            form = UserForm()
            return render(
                request,
                'shop/signup.html',{
                    'form':form
                })


    else:
        form = UserForm()
        return render(
            request,
            'shop/signup.html',{
                'form':form
            })


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
