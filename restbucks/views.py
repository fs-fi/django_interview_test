from django.shortcuts import render

from restbucks.models import  Product, Order,create_order
from restbucks.serializers import  ProductSerializer, OrderSerializer
from django.utils.encoding import smart_str
from django_fsm import can_proceed
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

class Products(APIView):
    permission_classes = (IsAuthenticated,)
    
    def get(self, request):
        queryset = Product.objects.all()
        product_serializer=ProductSerializer(queryset,many=True)
        return Response(product_serializer.data)

class Orders(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user_orders = Order.objects.filter(customer=request.user).all()
        order_serializer = OrderSerializer(user_orders, many=True)
        return Response(order_serializer.data)

    def post(self, request, *args, **kwargs):
        order = request.data.get("order")
        if order:
            create_order(request.user.id, order)
            return Response("Order created successfully",status=status.HTTP_200_OK)
        else:
            return Response("Operation failed",status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, *args, **kwargs):
        order = request.data.get("order")
        order_id = request.data.get("order_id")
        if order and order_id:
            create_order(request.user.id, order,order_id=order_id)
            return Response("Order updated successfully",status=status.HTTP_200_OK)
        else:
            return Response("Operation failed",status=status.HTTP_400_BAD_REQUEST)
    
    # cancel order
    def patch(self, request, *args, **kwargs):
        order_id = request.data.get("order_id")
        if order_id:
            state = request.data.get("state")
            order = Order.objects.filter(pk=order_id, customer=request.user).first()
            if order and state == "canceled" and can_proceed(order.cancel):
                order.cancel()
                order.save()
                return Response("Order canceled successfully",status=status.HTTP_200_OK)                       
            else:
                return Response("You are not allowed to cancel",status=status.HTTP_403_FORBIDDEN)
            
        else:
            return Response("Operation failed",status=status.HTTP_400_BAD_REQUEST)




