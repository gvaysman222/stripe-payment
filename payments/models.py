from django.db import models

class Item(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='usd')

    def __str__(self):
        return self.name


class Order(models.Model):
    items = models.ManyToManyField(Item, related_name='orders')
    created_at = models.DateTimeField(auto_now_add=True)
    stripe_payment_intent_id = models.CharField(max_length=100, blank=True, null=True)

    def total_amount(self):
        total = sum(item.price for item in self.items.all())
        discount_total = sum(d.amount for d in self.discounts.all())
        tax_total = sum(t.amount for t in self.taxes.all())
        return total - discount_total + tax_total

    def __str__(self):
        return f"Order #{self.pk}"


class Discount(models.Model):
    order = models.ForeignKey(Order, related_name='discounts', on_delete=models.CASCADE)
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Discount for Order {self.order.pk}"


class Tax(models.Model):
    order = models.ForeignKey(Order, related_name='taxes', on_delete=models.CASCADE)
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Tax for Order {self.order.pk}"
