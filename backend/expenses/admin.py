from django.contrib import admin

from .models import Expense, ExpenseShare

admin.site.register(Expense)
admin.site.register(ExpenseShare)
