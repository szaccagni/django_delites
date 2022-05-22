from django.shortcuts import redirect, render
from .models import Menu_Item,Ingredient,Sale,Recipe_Requirement
from django.views.generic import ListView
from django.db.models import ProtectedError, Sum
from django.db import IntegrityError
from datetime import date, timedelta
from django.contrib.auth import login,authenticate,logout
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.models import User



# Create your views here.
def index(request):
    if request.user.is_authenticated:
        today = str(date.today())
        tomorrow = str(date.today()+timedelta(1))
        revenue = Sale.objects.all().filter(dt_sold__range = [today,tomorrow]).aggregate(Sum('sale_amount'))['sale_amount__sum']
        start = str(date.today()- timedelta(7))
        end = str(date.today()+timedelta(1))
        sales = Sale.objects.all().filter(dt_sold__range = [start,end])
        popular = popThisWeek(sales)

        return render(request, "delites/home.html", {
            'user' : request.user.first_name,
            'revenue' : revenue,
            'popular' : popular
        })
    else:
        return redirect('login')


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        first = request.POST["first_name"]
        last = request.POST["last_name"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "delites/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password, first_name=first, last_name=last)
            user.save()
        except IntegrityError:
            return render(request, "delites/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "delites/register.html")

def login_view(request):
    if request.method == "POST":
        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "delites/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "delites/login.html")

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))

def popThisWeek(sales):
    menu_items = [item.item_name for item in Menu_Item.objects.all()]
    max = 0 
    max_item = ''
    for item in menu_items:
        count = sales.filter(item_sold__item_name = item).count()
        if int(count) > max:
            max = int(count)
            max_item = item
    return max_item
    

class MenuList(ListView):
    model = Menu_Item
    template_name = "delites/cur_menu.html"


def NewMenuItem(request):
    return render(request,'delites/new_menu_item.html')

def removeMenuItem(request):
    item_name = request.GET.get('item')
    menu_item = Menu_Item.objects.get(item_name=item_name)
    menu_item.delete()
    return redirect('curMenu')
    

def NewRecipe(request):
    all_ingredients = Ingredient.objects.all()
    if request.method == "POST":
        item_name = request.POST['menu_item']
    else: 
        item_name = item_name = request.GET.get('item')
        
    try:
        menu_item = Menu_Item.objects.get(item_name=item_name)
    except:
        item_price = request.POST['item_price']
        menu_item = Menu_Item(item_name=item_name,item_price=item_price)
        menu_item.save()

    try:
        requirements = Recipe_Requirement.objects.all().filter(menu_item=menu_item)
    except:
        requirements = []

    return render(request, 'delites/new_recipe.html', {
        'recipe_name' : item_name,
        'ingredients' :  all_ingredients,
        'requirements' : requirements
    })


def addIngredient(request):
    # grab variables
    ingredient_name = request.POST['ingredient']
    ingredient = Ingredient.objects.get(ingredient_name=ingredient_name)
    item_name = request.POST['menu_item']
    menu_item = Menu_Item.objects.get(item_name=item_name) 
    quant = request.POST['quant']
    # check if ingredient has already been added 
    try:
        requirement = Recipe_Requirement.objects.get(menu_item=menu_item,ingredient=ingredient)
        return NewRecipe(request)
    # if nothing is returned create recipe requirement record 
    except:
        new_requirement = Recipe_Requirement(menu_item=menu_item,ingredient=ingredient,quantity=quant)
        new_requirement.save()
        menu_item.ingredients.add(ingredient)
        menu_item.save()
        # reload new recipe page
        return NewRecipe(request)


def removeRequirement(request):
    # grab variables
    ingredient_name = request.GET.get('remove')
    item_name = request.GET.get('item')
    menu_item = Menu_Item.objects.get(item_name=item_name) 
    ingredient = Ingredient.objects.get(ingredient_name=ingredient_name)
    # if there are any issues removing the ingredient from the recipe the page will be reloaded with an error
    try:
        requirement = Recipe_Requirement.objects.get(menu_item=menu_item,ingredient=ingredient)
        requirement.delete()
        menu_item.ingredients.remove(ingredient)
        menu_item.save()
        error = ''
    except:
        error = 'there was an issue removing this ingredient'
    finally:
        menu_item = Menu_Item.objects.get(item_name=item_name) 
        all_ingredients = Ingredient.objects.all()
        requirements = Recipe_Requirement.objects.all().filter(menu_item=menu_item)
        # reload new recipe pg
        return render(request, 'delites/new_recipe.html', {
            'error' : error,
            'recipe_name' : menu_item,
            'ingredients' :  all_ingredients,
            'requirements' : requirements
        })


def newSale(request):
    items = Menu_Item.objects.all()
    return render(request, 'delites/new_sale.html', {
        'items' : items
    })

class sale_item:
    def __init__(self, name, price):
        self.name = name
        self.price = price

def make_sale_items(items):
    sales_items = items.split(",")
    sales_items.pop()
    list = []
    total = 0
    for item in sales_items:
        menu_item = Menu_Item.objects.get(item_name=item)
        price = menu_item.item_price
        total += price
        new_sale_item = sale_item(name=item,price=price)
        list.append(new_sale_item)
    return list, total

def addToSale(request):
    items = Menu_Item.objects.all()
    item = request.POST['item']
    items_str = request.POST['items_str']
    items_str += item + ','

    sales_items, total = make_sale_items(items_str)

    return render(request, 'delites/new_sale.html', {
        'items' : items,
        'items_str' : items_str,
        'sale_items' : sales_items,
        'total' : total
    })

def finalizeSale(request):
    items_str = request.POST['items_str'] 
    sales_items = items_str.split(",")
    sales_items.pop()
    for item in sales_items:
        menu_item = Menu_Item.objects.get(item_name=item)
        new_Sale = Sale(item_sold=menu_item)
        new_Sale.save()
    return redirect('salesHistory')

def salesHistory(request):
    sales = Sale.objects.all()
    return render(request, 'delites/sales_history.html', {
        'sales' : sales,
        'timeframe' : 'all'
    })

def filterSalesHistory(request):
    filter = request.POST['time_filter']
    if filter == 'all':
        sales = Sale.objects.all()
    elif filter == 'today':
        today = str(date.today())
        tomorrow = str(date.today()+timedelta(1))
        sales = Sale.objects.all().filter(dt_sold__range = [today,tomorrow])
    else:
        filter_int = int(filter)
        start = str(date.today()- timedelta(filter_int))
        end = str(date.today()+timedelta(1))
        sales = sales = Sale.objects.all().filter(dt_sold__range=[start,end])

    return render(request, 'delites/sales_history.html', {
        'sales' : sales,
        'timeframe' : filter
    })


def addInventory(request):
    if request.method == 'POST': 
        ingredient_name = request.POST['ingredient_name']
        quantity_availble = request.POST['quantity_availble']
        unit_price = request.POST['unit_price']
        unit_of_measure = request.POST['unit_of_measure']
        # ensure that the ingredient does not exist
        try:
            ingredient = Ingredient.objects.get(ingredient_name=ingredient_name)
            # return the page with an error message
            return render(request, 'delites/new_inventory_item.html', {
                'error': 'THIS INGREDIENT ALREADY EXISTS IN OUR INVENTORY',
                'item' : ingredient_name,
                'quant' : quantity_availble,
                'price' : unit_price,
                'measure' :unit_of_measure,
            })
        # if this ingredient does not already exist, create a new one
        except:
            new_ingredient = Ingredient(ingredient_name=ingredient_name, quantity_availble=quantity_availble,unit_price=unit_price,unit_of_measure=unit_of_measure)
            new_ingredient.save()
            return redirect('curInventory')

        # return render(request,'delites/test.html', {
        #     'test' : unit_of_measure
        # })
    else :
        return render(request, "delites/new_inventory_item.html")

def editInventory(request):
    if request.method == 'POST':
        ingredient_name_o = request.POST['original_name']
        ingredient_name = request.POST['ingredient_name']
        quantity_availble = request.POST['quantity_availble']
        unit_price = request.POST['unit_price']
        unit_of_measure = request.POST['unit_of_measure']

        try:
            ingredient = Ingredient.objects.get(ingredient_name=ingredient_name_o)
            ingredient.ingredient_name = ingredient_name
            ingredient.quantity_availble = quantity_availble
            ingredient.unit_price = unit_price
            ingredient.unit_of_measure = unit_of_measure
            ingredient.save()
            return redirect('curInventory')
        except:
            return render(request, 'delites/edit_inventory_item.html', {
                'error' : 'there was an error with this update',
                'item_o' : ingredient_name_o,
                'item' : ingredient_name,
                'quant' : quantity_availble,
                'price' : unit_price,
                'measure' : unit_of_measure,

            })

    else:
        inventory_name = request.GET.get('inventory')
        inventory = Ingredient.objects.get(ingredient_name=inventory_name)
        return render(request, 'delites/edit_inventory_item.html', {
            'item_o' : inventory.ingredient_name,
            'item' : inventory.ingredient_name,
            'quant' : inventory.quantity_availble,
            'price' : inventory.unit_price,
            'measure' : inventory.unit_of_measure,
        })

def deleteInventory(request):
    inventory_name = request.GET.get('inventory')
    inventory = Ingredient.objects.get(ingredient_name=inventory_name)
    try:
        inventory.delete()
    except ProtectedError:
        inventory = Ingredient.objects.all()
        return render(request, 'delites/cur_inventory.html', {
        'ingredients' : inventory,
        'error' : f'looks like the ingrdient, {inventory_name}, is used in one or more recipes, you cannot remove'
        })
    return redirect('curInventory')
    

def curInventory(request):
    inventory = Ingredient.objects.all()
    return render(request, 'delites/cur_inventory.html', {
        'ingredients' : inventory
    })


def getFinancials(request):
    revenue = Sale.objects.aggregate(Sum('sale_amount'))['sale_amount__sum']
    cost = Ingredient.objects.aggregate(Sum('item_cost'))['item_cost__sum']
    cost = round(cost,2)
    profits = revenue - cost

    return render(request, 'delites/getFinancials.html', {
        'revenue' : revenue,
        'cost' : cost,
        'profits' : profits
    })



