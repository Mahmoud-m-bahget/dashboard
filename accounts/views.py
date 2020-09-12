from django.shortcuts import render , redirect
from .models import *
from .forms import OrderForm , CreateUserForm , ProductForm ,CustomerForm ,UserForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth import authenticate , login , logout
from django.contrib.auth.decorators import login_required
from .decorators import unauthenticated_user ,allwoed_users ,admin_only
from django.contrib.auth.models import Group
from django.forms import inlineformset_factory
from .filters import OrderFilter
# Create your views here.

@unauthenticated_user
def refisterPage(request):
    form = CreateUserForm()
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request , 'Account was created for ' + username)
            return redirect('login')
    context = {
        'form':form
    }
    return render(request ,'accounts/register.html', context)
@unauthenticated_user
def loginPage(request):
    if request.method == 'POST':
        username= request.POST.get('username')
        password= request.POST.get('password')
        user = authenticate(request , username = username , password = password)

        if user is not None:
            login(request , user)
            return redirect('home')

        else:
            messages.info(request , 'Username OR password is incorrect')
    context = {
    }
    return render(request ,'accounts/login.html', context)

def logoutuser(request):
    logout(request)
    return redirect('login')


@login_required(login_url='login')
@admin_only
def home(request):
    orders = Order.objects.all()
    customers = Customer.objects.all()
    total_orders = orders.count()
    total_customer = customers.count()
    delivered = orders.filter(status='Delivered').count()
    pending = orders.filter(status='Pending').count()

    context = {
        'orders':orders,
        'customers':customers,
        'total_orders':total_orders,
        'total_customer':total_customer,
        'delivered':delivered,
        'pending':pending,
    }
    return render(request , 'accounts/dashboard.html',context)

@login_required(login_url='login')
@allwoed_users(allowed_roles=['customer'])
def userpage(request):
    orders = request.user.customer.order_set.all()
    total_orders = orders.count()
    delivered = orders.filter(status='Delivered').count()
    pending = orders.filter(status='Pending').count()

    context = {
        'orders':orders ,
        'total_orders':total_orders,
        'delivered':delivered,
        'pending':pending,
    }
    return render(request , 'accounts/user.html' , context)


@login_required(login_url='login')
@allwoed_users(allowed_roles=['customer'])
def accountSettings(request):
    customer = request.user.customer
    form = CustomerForm(instance=customer)
    if  request.method == 'POST':
        form = CustomerForm(request.POST,request.FILES, instance=customer)
        if form.is_valid():
            form.save()

    user = request.user
    userform = UserForm(instance=user)
    if  request.method == 'POST':
        userform = UserForm(request.POST,request.FILES, instance=user)
        if userform.is_valid():
            userform.save()
        
    context = {'form':form,'userform':userform}

    return render (request ,'accounts/accounts_settings.html' , context)

@login_required(login_url='login')
@allwoed_users(allowed_roles=['admin'])
def product(request):
    products = Product.objects.all()
    return render(request , 'accounts/product.html',{'products':products})

@login_required(login_url='login')
@allwoed_users(allowed_roles=['admin'])
def createProduct(request):
    product = Product.objects.all()
    form = ProductForm(initial={'product':product})
    if request.method =='POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('product')

    context = {'form':form}
    return render(request ,'accounts/product_form.html', context)

@login_required(login_url='login')
@allwoed_users(allowed_roles=['admin'])
def updateproduct(request, pk):
    product = Product.objects.get(id = pk)
    form = ProductForm(instance=product)
    if request.method =='POST':
        form = ProductForm(request.POST , instance=product)
        if form.is_valid():
            form.save()
            return redirect('product')

    context = {'form':form}
    return render(request ,'accounts/product_form.html', context)


@login_required(login_url='login')
@allwoed_users(allowed_roles=['admin'])
def deleteProduct(request , pk):
    product = Product.objects.get(id = pk)
    if request.method == "POST":
        product.delete()
        return redirect('product')

    context={
        'item':product
    }
    return render(request,'accounts/delete_product.html',context)

@login_required(login_url='login')
@allwoed_users(allowed_roles=['admin'])
def customer(request , pk):
    customer = Customer.objects.get(id = pk)
    orders = customer.order_set.all()
    orders_count = orders.count()
    myFilter = OrderFilter(request.GET , queryset= orders)
    orders = myFilter.qs
    context ={
        'customer':customer,
        'orders':orders,
        'orders_count':orders_count,
        'myFilter':myFilter
    }
    return render(request , 'accounts/customer.html',context)

@login_required(login_url='login')
@allwoed_users(allowed_roles=['admin'])
def createOrder(request,pk):
    OrderFormSet = inlineformset_factory(Customer,Order,fields=('product','status'),extra=1)
    customer = Customer.objects.get(id = pk)
    formset = OrderFormSet(queryset=Order.objects.none(),instance=customer)
    if request.method =='POST':
        formset = OrderFormSet(request.POST , instance=customer)
        if formset.is_valid():
            formset.save()
            return redirect('/')

    context = {'formset':formset}
    return render(request ,'accounts/order_form.html', context)


@login_required(login_url='login')
@allwoed_users(allowed_roles=['admin'])
def updateOrder(request, pk):
    order = Order.objects.get(id = pk)
    form = OrderForm(instance=order)
    if request.method =='POST':
        form = OrderForm(request.POST , instance=order)
        if form.is_valid():
            form.save()
            return redirect('/')

    context = {'form':form}
    return render(request ,'accounts/order_form.html', context)

@login_required(login_url='login')
@allwoed_users(allowed_roles=['admin'])
def deleteOrder(request , pk):
    order = Order.objects.get(id = pk)
    if request.method == "POST":
        order.delete()
        return redirect('/')


    context={
        'item':order
    }
    return render(request,'accounts/delete.html',context)