from .utils import parse_col, remove_commas
import re
from django.http import JsonResponse

def parse_schema(physical_plan: str):
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
            location = re.findall(r'\[(.*?)\]', lines[3])[0]            # расположение файла
            results = re.findall(r'\[(.*?)\]', lines[1])[1] # все колонки которые ссылаются на этот файл
            # добавляем спаршенную колонку в наш словарь
            for result in results.split(", "):
                col = parse_col(result)
                input_cols.add(col)
                all_cols.add(col)
                col_to_location[col] = f"{location}.{col}"

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
                    for word in left.replace("(", " ").replace(")", " ").split():
                        # в интересующей нас колонке содержится #, но сама начинается с #
                        if not word.startswith("#") and "#" in word:
                            if not right.startswith("_"):
                                child_col = parse_col(right)
                            else:
                                child_col = right
                            all_cols.add(child_col)
                            if not word.startswith("_"):
                                parent_col = parse_col(word)
                            else:
                                parent_col = word
                            all_cols.add(parent_col)
                            if child_col == parent_col:
                                continue
                            if child_col not in dependencies:
                                dependencies[child_col] = {parent_col}
                            else:
                                dependencies[child_col].add(parent_col)
    graph = dict()
    graph["graph"] = {"nodes": [], "links": []}

    for col in all_cols:
        node = {"id": col}
        if col in input_cols and col in output_cols:
            node["color"] = "green"
        elif col in input_cols:
            node["color"] = "red"
        elif col in output_cols:
            node["color"] = "blue"
        if col in col_to_location.keys():
            node["location"] = col_to_location[col]
        graph["graph"]["nodes"].append(node)

    for child, parents in dependencies.items():
        for parent in parents:
            node = {"source": parent, "target": child}
            graph["graph"]["links"].append(node)

    # with open("graph.json", "w") as outfile:
    #     json.dump(graph, outfile, indent=4)
    
    return graph
    
    #return dependencies, col_to_location, input_cols, output_cols

