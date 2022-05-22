from django.contrib import admin
from .models import Menu_Item,Ingredient,Sale,Recipe_Requirement

class IngredientAdmin(admin.ModelAdmin):
    list_display = ("ingredient_name","quantity_availble", "unit_price", "item_cost", "unit_of_measure")

class Menu_ItemAdmin(admin.ModelAdmin):
    list_display = ("item_name", "item_price")

class Recipe_RequirementAdmin(admin.ModelAdmin):
    list_display = (Recipe_Requirement.__str__, "menu_item")

class SaleAdmin(admin.ModelAdmin):
    list_display = ("item_sold", "sale_amount", "dt_sold")

# Register your models here.
admin.site.register(Ingredient,IngredientAdmin)
admin.site.register(Menu_Item,Menu_ItemAdmin)
admin.site.register(Recipe_Requirement,Recipe_RequirementAdmin)
admin.site.register(Sale, SaleAdmin)