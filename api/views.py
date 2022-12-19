from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from .serializers import *
from .models import *
import datetime

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
            orders = Order.objects.filter(customer = user, complete = False)
            for order in orders:
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
        order, created = Order.objects.get_or_create(customer = customer, complete = False)
        orderItem = OrderItem.objects.create(order = order, product = product)
        serializer = OrderItemSerializer(orderItem, data= request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ShippingDetails(APIView):
    def get(self, request):
        customer = request.user.customer
        orders = Order.objects.filter(customer=customer, complete = True)
        data = []
        for order in orders:
            shipping = ShippingAddress.objects.filter(order=order)
            serializer = ShippingSerializer(shipping, many = True)
            data.append(serializer.data)
        return Response(data)
    def post(self, request):
        customer = request.user.customer
        order = Order.objects.get(customer=customer, complete = False)
        transactoinID = datetime.datetime.now().timestamp()
        order.transaction_id = transactoinID
        shipping = ShippingAddress.objects.create(customer=customer, order = order)
        serializer = ShippingSerializer(shipping, data= request.data)
        orderItems = OrderItem.objects.filter(order= order)
        items = []
        for orderItem in orderItems:
            items.append({
                "prodcutName": orderItem.product.name,
                "quantity": orderItem.quantity,
                "price": orderItem.get_total
            })
        if serializer.is_valid():
            order.complete = True
            order.save()
            serializer.save()
            context = {
                "transctionId": order.transaction_id,
                "data":serializer.data,
                "orderedItems":items,
                "total": order.get_cart_total

            }
        return Response(context, status=status.HTTP_201_CREATED)
    
