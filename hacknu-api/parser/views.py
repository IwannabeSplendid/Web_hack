
from rest_framework.decorators import api_view

from .parser import parse_schema
from django.http import JsonResponse
import os
from ..settings import BASE_DIR

# Save the physical plan that we need to parser in hacknu-api/parser/src folder
path_to_src = BASE_DIR / 'hacknu-api/parser/src'

def get_graph_from_physical_plan(name_plan: str, id: int):
    path = path_to_src / name_plan
    # Reading the physical plan
    f = open(path, "r")
    physical_plan = f.read()
    # Parsing the physical plan
    result =  parse_schema(physical_plan, name_plan, id)
    
    return result
    
    
@api_view(['GET'])
def parse(request):
    result = []
    
    files = os.listdir(path_to_src)
    try:
        files.remove('.DS_Store')
    except:
        pass

    for i, file in enumerate(files):
        result.append(get_graph_from_physical_plan(file, i))    
    
    return JsonResponse(result, safe=False)
     


