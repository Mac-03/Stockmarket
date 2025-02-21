from django.shortcuts import render,HttpResponse,redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Watchlist
import requests
import time
# Create your views here.
@login_required(login_url='login')
def HomePage(request):
    return render (request,'stock_form.html')

def SignupPage(request):
    if request.method=='POST':
        uname=request.POST.get('username')
        email=request.POST.get('email')
        pass1=request.POST.get('password1')
        pass2=request.POST.get('password2')

        if pass1!=pass2:
            return HttpResponse("Your password and confrom password are not Same!!")
        else:

            my_user=User.objects.create_user(uname,email,pass1)
            my_user.save()
            return redirect('login')
        



    return render (request,'signup.html')

def LoginPage(request):
    if request.method=='POST':
        username=request.POST.get('username')
        pass1=request.POST.get('pass')
        user=authenticate(request,username=username,password=pass1)
        if user is not None:
            login(request,user)
            return redirect('home')
        else:
            return HttpResponse ("Username or Password is incorrect!!!")

    return render (request,'login.html')

def LogoutPage(request):
    logout(request)
    return redirect('login')
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import yfinance as yf
from django.shortcuts import render
from twilio.rest import Client

account_sid = 'AC0d28848c5fbde2c19786596d806dae4c'
auth_token = '38b955661cd95bb46a336849fbbb38be'
client = Client(account_sid, auth_token)


@csrf_exempt
def check_price_target(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode("utf-8"))  # Correctly parse JSON payload
            stock_name = data.get("stockName")
            target_price = data.get("targetPrice")
            stop_loss_price = data.get("stopLossPrice")

            if not stock_name or not target_price or not stop_loss_price:
                return JsonResponse({"success": False, "message": "All fields are required."}, status=400)

            # Fetch the current stock price using yfinance
            stock = yf.Ticker(f"{stock_name}.NS")
            stock_info = stock.info
            current_price = stock_info.get("currentPrice", None)

            if current_price is None:
                return JsonResponse({"success": False, "message": "Could not fetch the stock price."}, status=400)

            # Check against target and stop-loss prices
            if current_price >= float(target_price):
                body_msg = f"{stock_name} target price reached. Your target:{target_price} current price :{current_price}"
                message = client.messages.create(
                from_='+15855410656',
                body=body_msg,
                to='+917207138327'
                )
                return JsonResponse({"success": True, "message": f"Target price reached for {stock_name}!"})
                
            elif current_price <= float(stop_loss_price):
                body_msg = f"{stock_name} stop loss price reached"
                message = client.messages.create(
                from_='+15855410656',
                body=body_msg,
                to='+917207138327'
                )
                return JsonResponse({"success": True, "message": f"Stop loss triggered for {stock_name}!"})
                
            else:
                return JsonResponse({"success": True, "message": f"Current price of {stock_name} is ₹{current_price:.2f}"})
        except json.JSONDecodeError:
            return JsonResponse({"success": False, "message": "Invalid JSON payload."}, status=400)
        except Exception as e:
            return JsonResponse({"success": False, "message": f"Error: {str(e)}"}, status=500)
    else:
        return JsonResponse({"success": False, "message": "Invalid request method."}, status=405)


@csrf_exempt

def get_stock_price(request):
    stock_name = request.GET.get("stockName")
    if not stock_name:
        return JsonResponse({"success": False, "message": "Stock name is required."}, status=400)

    retries = 3  # Number of retry attempts

    for attempt in range(retries):
        try:
            stock = yf.Ticker(f"{stock_name}.NS")
            stock_info = stock.info
            current_price = stock_info.get("currentPrice", None)

            if current_price is not None:
                return JsonResponse({"success": True, "current_price": round(current_price, 2)})
            
            else:
                return JsonResponse({"success": False, "message": "Could not fetch the stock price."}, status=400)
        
        except Exception as e:
            if "429" in str(e) or "Too Many Requests" in str(e):
                time.sleep(5)  # Wait 5 seconds before retrying
                continue  # Retry again
            else:
                return JsonResponse({"success": False, "message": f"Error: {str(e)}"}, status=500)

    return JsonResponse({"success": False, "message": "Request limit exceeded. Try again later."}, status=429)

@csrf_exempt
def get_indices(request):
    try:
        # Fetch Sensex and Nifty values
        sensex_ticker = yf.Ticker("BSESN")
        nifty_ticker = yf.Ticker("NSEI")

        # Get the info dictionary
        sensex_info = sensex_ticker.info
        nifty_info = nifty_ticker.info

        # Check for available fields
        sensex_price = sensex_info.get('currentPrice') or sensex_info.get('last_price') or sensex_info.get('regularMarketPrice')
        nifty_price = nifty_info.get('currentPrice') or nifty_info.get('last_price') or nifty_info.get('regularMarketPrice')

        if sensex_price is None or nifty_price is None:
            return JsonResponse({"success": False, "message": "Could not fetch the stock prices."}, status=400)

        return JsonResponse({
            "success": True,
            "sensex": round(sensex_price, 2),
            "nifty": round(nifty_price, 2)
        })
    except Exception as e:
        return JsonResponse({"success": False, "message": f"Error: {str(e)}"}, status=500)
def fetch_stock_data(request):
    response = requests.get('API_URL_FOR_SENSEX_AND_NIFTY')
    data = response.json()
    sensex_value = data['sensex']  # Adjust based on API response structure
    nifty_value = data['nifty']      # Adjust based on API response structure
    return JsonResponse({'sensex': sensex_value, 'nifty': nifty_value})
from django.shortcuts import render, redirect
from .models import Watchlist
from django.contrib.auth.decorators import login_required  # Ensure the user is logged in

@login_required
def add_to_watchlist(request):
    if request.method == 'POST':
        stock_name = request.POST.get('stock_name')
        target_price = request.POST.get('target_price')
        stop_loss_price = request.POST.get('stop_loss_price')
        
        # Save the data to the database
        watchlist_item = Watchlist(
            user=request.user,  # Use the logged-in user
            stock_name=stock_name,
            target_price=target_price,
            stop_loss_price=stop_loss_price
        )
        watchlist_item.save()

         # Redirect to the watchlist page

    return render(request, 'stock_form.html')  # Render the form for adding stocks
