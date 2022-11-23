from cProfile import Profile
import email
from django.contrib import messages
from urllib import request
from urllib.request import Request
from django.shortcuts import render, redirect
from django.contrib.auth.models import auth
from django.contrib.auth import authenticate,login,logout
from django.http import HttpResponse ,JsonResponse
# Create your views here.
from .helpers import *
from .models import Account 
import datetime 
from orders.models import Orders
from django.db.models import Count,Sum,Q

def d_admin(request):
    if request.user.is_superuser:
        today = datetime.datetime.now()
        current = today.strftime("%B %d, %Y")
        
        date = Orders.objects.filter(orderd_date__month = today.month).values("orderd_date__date").annotate(orderd_items=Count('id')).order_by(
            "orderd_date__date")
        sales = Orders.objects.filter(orderd_date__month = today.month).values("orderd_date__date").annotate(
            sales=Count('id',filter=Q(status ="Deliverd")),cancelled=Count('id' , filter=Q(status ="cancelled")),returns=Count('id' , filter=(Q(
                status ="Refund In Progress")|Q(status ="Return Aproved")))).order_by("orderd_date__date")
        
        
        
        
        return render(request, "admin/index.html" ,{'date':date, 'sales':sales , 'current':current})
    return redirect("adminlogin")

def home(request):
    if request.user.is_authenticated:
        return render(request, "index.html")
   
        
    return render(request, "index.html")

def user_login(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.POST:
        email = request.POST.get("email")
        password = request.POST.get("password")
        if not email or not password :
            messages.error(request, 'Email and Password is required !!')
            return redirect(request.META.get('HTTP_REFERER'))
        check = Account.objects.filter(email=email).exists()
        if check==False:
            messages.error(request, 'email does not exists !')
        if check:
            user = authenticate(request, email=email,password=password)
            if user is not None :
                if user.is_blocked is True:
                    messages.error(request, 'Sorry, You have been Blocked by admin !!')
                    return redirect(request.META.get('HTTP_REFERER'))
                login(request,user)
                return redirect("home")
        
            messages.info(request, 'Invalid Password !!')
              
    return render(request,"login.html")

def user_signup(request,*args, **kwargs):
    
    user = request.user
    if user.is_authenticated:
        return redirect("home")
    try:
            if request.POST:
                first_name= request.POST.get("first_name")
                last_name= request.POST.get("last_name")
                email = request.POST.get("email")
                phone_number = request.POST.get("phone_number")
                username = request.POST.get("username")
                password = request.POST.get("password1")
                
                if not first_name or not email or not phone_number or not username or not password:
                    messages.error(request,'Please fill all required fields')
                    return redirect(request.META.get('HTTP_REFERER'))
                
                if Account.objects.filter(phone_number=phone_number).exists():
                    messages.info(request,'a user with this phone number is already exist')
                    return redirect ('user_signup')
                if Account.objects.filter(username=username).exists():
                    messages.info(request,'username is already taken')
                    return redirect ('user_signup')
                if Account.objects.filter(email=email).exists():
                    messages.info(request, 'An account with this email is already exist')
                    return redirect ('user_signup')
                user = Account.objects.create_user(first_name=first_name,last_name=last_name,
                                                   email=email,username= username,
                                                   phone_number=phone_number,
                                                   password=password)
                user.save()
                user = Account.objects.get(email=email,username=username)
                user1 = authenticate(request,email=email,password=password)
                if user1 is not None:
                    otp_handler = otphandler('9544633437').sent_otp_on_phone() # give phone_number instead of real numbers 
                    signupgetuser(email)
                    return redirect("signup_otp_v")
                
            
    except:
        messages.info(request,'Invalid credentials')
    return render(request,"signup.html")

def signup_otp_v(request):
    user = request.user
    print(user)
    if user.is_authenticated:
        return redirect("home")
    email = signupgetuser.email
    

    try:
        otp = otphandler.Otp
        if request.method == "POST":
            otp1 = request.POST.get("otp1")
            otp2 = request.POST.get("otp2")
            otp3 = request.POST.get("otp3")
            otp4 = request.POST.get("otp4")
            if not otp1 or not otp2 or not otp3 or not otp4:
                messages.error(request,'make sure you filled all fields !!')
                return redirect(request.META.get('HTTP_REFERER'))
            otp5 = otp1+otp2+otp3+otp4
            user = Account.objects.get(email=email)
            if otp == otp5:
                login(request,user)
                return render(request,"index.html")
            else:
                messages.error(request,'Invalid otp, make sure it is correct !!')
                return redirect(request.META.get('HTTP_REFERER'))   
    except:
        messages.error(request,'Invalid credentials !!')
        
    return render (request, "signup_otpv.html")

def user_otp(request):
    if request.user.is_authenticated:
      return redirect("home")
    try: 
        if request.POST:
            phone_number = request.POST.get("phone_number")
            phone=Account.objects.filter(phone_number=phone_number).exists()
            if phone is True:
                user = Account.objects.get(phone_number=phone_number)
                request.user = user
                otp_handler = otphandler(phone_number).sent_otp_on_phone()
                return redirect("otp_v")
    except:
       pass
    return render(request,'otp.html')

def otp_v(request):
    if request.user.is_authenticated:
         return redirect("home")
    phone = otphandler.phone_number
    user = Account.objects.get(phone_number=phone)
    request.user = user
    try:    
        user =request.user
        otp = otphandler.Otp
        if request.method == "POST":
            otp1 = request.POST.get("otp1")
            otp2 = request.POST.get("otp2")
            otp3 = request.POST.get("otp3")
            otp4 = request.POST.get("otp4")
            if not otp1 or not otp2 or not otp3 or not otp4:
                messages.error(request,'make sure you filled all fields !!')
                return redirect(request.META.get('HTTP_REFERER'))
            otp5 = otp1+otp2+otp3+otp4
            if otp == otp5:
                login(request,user)
                return render(request,"index.html")
            else:
                messages.error(request,'Invalid otp, make sure it is correct !!')
                return redirect(request.META.get('HTTP_REFERER'))   
    except:
        messages.error(request,'Invalid credentials !!')
    return render (request, "otpv.html" )

def resendotp(request):
    phone = otphandler.phone_number
    otphandler(phone).sent_otp_on_phone()
    return JsonResponse({phone:phone})

def adminlogin(request):
    if request.POST:
        email= request.POST.get("email")
        password = request.POST.get("password")
        user = authenticate(request,email=email,password=password)
        if user is not None:
            if user.is_superuser is True:
               login(request,user)
               return redirect("d_admin")
    return render (request, "admin/login.html")

def adminlogout(request):
    logout(request)
    return redirect(adminlogin)

def log_out(request):
    logout(request)
    return render(request, "login.html")

def log_in(request):
    return redirect('user_login')