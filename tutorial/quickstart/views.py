
from rest_framework.response import Response
from rest_framework.decorators import api_view

from .parser import parse_schema
from django.http import JsonResponse
import os



    
@api_view(['GET'])
def parse(request):
    path1 = os.getcwd() + "/tutorial/quickstart/src/first_text.txt"
    path2 = os.getcwd() + "/tutorial/quickstart/src/second_text.txt"
    path3 = os.getcwd() + "/tutorial/quickstart/src/third_text.txt"
    
    
    f1 = open(path1, "r")
    physical_plan1 = f1.read()
    
    f2 = open(path2, "r")
    physical_plan2 = f2.read()
    
    f3 = open(path3, "r")
    physical_plan3 = f3.read()
    
    
    result1 =  parse_schema(physical_plan1, "first_text",1)
    result2 =  parse_schema(physical_plan2, "second_text",2)
    result3 =  parse_schema(physical_plan3, "third_text",3)
    
    result = [result1, result2, result3]
    
    
    return JsonResponse(result, safe=False)
     
    # return Response({"message": "Hello, world!"})

