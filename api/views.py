from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from .serializers import *
from .models import *

# Create your views here.

class ProductList(APIView):
    def get(self, request):
        products = Product.objects.all()
        serializer = ProductSerializer(products, many = True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class CartItem(APIView):
    def get(self, request):
        user = request.user.customer
        context = {

                "data":[],
                "cart-items": 0,
                "cart-total": 0,
                
            }
        try:
            order = Order.objects.get(customer = user)
            if order.complete == True:
                return Response("No Orders")
            orderItems = OrderItem.objects.filter(order=order)
            context["cart-total"] = order.get_cart_total
            context["cart-items"] = order.get_cart_items
            for orderItem in orderItems:
                context["data"].append( {
                    'product-name': orderItem.product.name,
                    'quantity': orderItem.quantity,
                    'price': orderItem.product.price,
                    'total':orderItem.get_total
                })
        except:
            context["message"] = "No data available"
            
        return Response(context, status=status.HTTP_200_OK)

class AddCartItems(APIView):
    def post(self, request, id):
        print(id, request.user.customer)
        customer = request.user.customer
        product = Product.objects.get(id = id)
        order, created = Order.objects.get_or_create(customer = customer)
        orderItem = OrderItem.objects.create(order = order, product = product)
        serializer = OrderItemSerializer(orderItem, data= request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
