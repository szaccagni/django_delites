from django.urls import path
from . import views

urlpatterns = [
    path("register", views.register, name="register"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("", views.index, name="index"),
    path("new_menu_item", views.NewMenuItem, name="newMenuItem"),
    path("cur_menu",views.MenuList.as_view(), name="curMenu"),
    path("removeMenuItem",views.removeMenuItem,name="removeMenuItem"),
    path("new_recipe", views.NewRecipe, name="newRecipe"),
    path("addIngredient", views.addIngredient, name="addIngredient"),
    path("removeRequirement", views.removeRequirement, name="removeRequirement"),
    path("new_sale", views.newSale, name="newSale"),
    path("addToSale", views.addToSale, name="addToSale"),
    path("finalizeSale", views.finalizeSale, name="finalizeSale"),
    path("sales_history", views.salesHistory, name="salesHistory"),
    path("filterSalesHistory", views.filterSalesHistory, name="filterSalesHistory"),
    path("addInventory", views.addInventory, name="addInventory"),
    path("editInventory",views.editInventory, name="editInventory"),
    path("deleteInventory", views.deleteInventory, name="deleteInventory"),
    path("cur_inventory", views.curInventory,name="curInventory"),
    path("getFinancials", views.getFinancials, name='getFinancials')
]