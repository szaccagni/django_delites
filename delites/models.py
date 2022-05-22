from django.db import models


# Create your models here.
class Ingredient(models.Model):
    quantity_availble = models.DecimalField(default=0, max_digits=6, decimal_places=2)
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)
    ingredient_name = models.CharField(max_length=255)
    item_cost = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    
    measurements = [
        ('g','grams'),
        ('oz','ounces'),
        ('wh','whole units')
    ]   
    unit_of_measure = models.CharField(max_length=2,choices=measurements,default='wh')
    
    def __str__(self):
        return f"{self.ingredient_name} ({self.unit_of_measure})"

    def save(self, *args, **kwargs):
        self.item_cost = float(self.quantity_availble) * float(self.unit_price)
        super().save(*args, **kwargs)


class Menu_Item(models.Model):
    item_price = models.DecimalField(max_digits=6, decimal_places=2)
    item_name = models.CharField(max_length=255)
    ingredients = models.ManyToManyField(Ingredient, blank=True)

    def __str__(self):
        return f"{self.item_name}"


class Recipe_Requirement(models.Model):
    menu_item = models.ForeignKey(Menu_Item, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.PROTECT)
    quantity = models.DecimalField(default=0, max_digits=6, decimal_places=2)

    def __str__(self):
        measure = self.ingredient.unit_of_measure if self.ingredient.unit_of_measure != 'wh' else ''
        quantity_description = str(self.quantity).rstrip("0").rstrip(".") +" "+ measure
        return f"{quantity_description} {self.ingredient.ingredient_name}"


class Sale(models.Model):
    item_sold = models.ForeignKey(Menu_Item, on_delete=models.CASCADE)
    dt_sold = models.DateTimeField(auto_now_add=True, blank=True)
    sale_amount = models.DecimalField(default=0, max_digits=6, decimal_places=2)

    def __str__(self):
        return f"{self.item_sold} - {self.dt_sold}"

    def save(self, *args, **kwargs):
        if self.sale_amount == 0:
            self.sale_amount = self.item_sold.item_price

            requirements = Recipe_Requirement.objects.all().filter(menu_item=self.item_sold)
            for item in requirements:
                ingredient = item.ingredient
                ingredient.quantity_availble -= item.quantity
                ingredient.save()

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return 'sales_history'
    
    class Meta:
        ordering = ['-dt_sold']