from .utils import parse_col, remove_commas
import re
import networkx as nx
from django.http import JsonResponse

def parse_schema(physical_plan: str, filename: str):
    """
    Входные данные:
        physical_plan: текст физического плана для датафрейма
        columns: лист содержащий все колонки в новосозданном датафрейме
    Выходные данные:
        parsed: ответ
    """

    col_to_location = dict()    # мапает колонки в файл который им соответствует
    dependencies = dict()       # мапает одну колонку в лист с которыми он зависим
    parsed = dict()             # ответ который нам нужно вывести
    input_cols = set()          # сет со всеми входными колонками
    output_cols = set()         # сет со всеми выходными колонками
    all_cols = set()

    # отделяем == Physical Plan == от остального текста
    schema = physical_plan.split("\n\n\n")[1]
    # делим оставшийся текст схемы на отдельные методы 
    splitted_schema = schema.split("\n\n")
    for split in splitted_schema:
        lines = split.split("\n")       # все линии в отдельном сплите
        command = lines[0].split()[1]   # команда для сплита

        if command == "Scan":
            # расположение файла
            location = re.findall(r'\[(.*?)\]', lines[3])[0]
            # все колонки которые ссылаются на этот файл
            results = re.findall(r'\[(.*?)\]', lines[1])[1]
            # добавляем спаршенную колонку в наш словарь
            for result in results.split(", "):
                col = parse_col(result)
                input_cols.add(col)
                all_cols.add(col)
                col_to_location[col] = location

        elif command == "AdaptiveSparkPlan":
            outputs = re.findall(r'\[(.*?)\]', lines[1])[1]
            for output in outputs.split(", "):
                col = parse_col(output)
                all_cols.add(col)
                output_cols.add(col)
            
        elif command != "Window":
            # в сплите берем только те линии в которых есть AS
            for line in filter(lambda x: " AS " in x, lines):
                # достаем все содержимое внутри квадратных скобок
                results = re.findall(r'\[(.*?)\]', line)[1]
                results = remove_commas(results)
                for result in results.split(", "):
                    # берем только те элементы в которых есть AS
                    try: left, right = result.split(" AS ")
                    except: continue
                    # заменяем скобочки на пробелы и ищем название колонки
                    words = left.replace("(", " ").replace(")", " ").split()
                    for word in words:
                        # в интересующей нас колонке содержится #, но сама начинается с #
                        if (not word.startswith("#") and "#" in word) or len(words) == 1:
                            child_col = parse_col(right)
                            all_cols.add(child_col)
                            parent_col = parse_col(word)
                            all_cols.add(parent_col)
                            # скипаем случаи когда нод отсылается на самого себя
                            if child_col == parent_col:
                                continue
                            # делаем parent_col родителем child_col
                            if child_col not in dependencies:
                                dependencies[child_col] = {parent_col}
                            else:
                                dependencies[child_col].add(parent_col)
    
    # создаем словарь содержащий информацию о графе который будем джсонифировать
    json_file = dict()
    json_file["graph"] = {"nodes": [], "links": []}

    for col in all_cols:
        node = {"id": col}
        # задаем цвета вершинам графа
        if col in input_cols and col in output_cols:
            node["color"] = "green"
        elif col in input_cols:
            node["color"] = "red"
        elif col in output_cols:
            node["color"] = "blue"
        # инфа о локации которая будет отображаться при нажатии на нод
        if col in col_to_location.keys():
            node["location"] = col_to_location[col]
        json_file["graph"]["nodes"].append(node)

    # вводим связи вершин графа в json_file
    for child, parents in dependencies.items():
        for parent in parents:
            node = {"source": parent, "target": child}
            json_file["graph"]["links"].append(node)

    dependencies_inverse = []
    for key, val in sorted(dependencies.items()):
        for j in val:
            dependencies_inverse.append((j, key))

    nx_graph = nx.DiGraph()
    nx_graph.add_edges_from(dependencies_inverse)
    answer = {}
    for child, parents in sorted(dependencies.items()):
        if child not in output_cols:
            continue
        ancestors_dict = list(nx.ancestors(nx_graph, child))
        answer[child] = {
            'data_sources' : set(),
            'cols_dependencies': set()
        }
        for ancestor in ancestors_dict:
            if ancestor in input_cols:
                if ancestor in col_to_location:
                    location_modified = f"{col_to_location[ancestor]}.{ancestor}"
                else:
                    location_modified = f"null_file.{ancestor}"
                answer[child]['data_sources'].add(col_to_location[ancestor])
                answer[child]['cols_dependencies'].add(location_modified)
            
    json_file["id"] = 1
    json_file["filename"] = filename
    json_file["code"] = str(answer)
    
    return json_file