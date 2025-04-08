from django.shortcuts import render

from rest_framework import permissions, generics
from rest_framework.response import Response
from django.db.models import Sum

from cart.models import Order, CartItem
from inventorymanagement.views import IsVendor



