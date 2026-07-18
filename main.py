import ast
import os
import sys
import re
from pydantic import BaseModel



class Chunk(BaseModel):
    file_name: str
    start: int
    end: int
    content: str
    typee: str


def chunking_docs(file_path, conten):
    res = []
    chunk = ""
    offset = 0

    if len(conten) < 2000:
        obj = Chunk(file_name=file_path, start=0, end=len(conten),
                    content=conten, typee="text")
        res.append(obj)
        return res

    lines = re.split(r"\n\n", conten)
    for line in lines:

        if len(line) + len(chunk) < 2000:
            chunk += line

        else:
            obj = Chunk(file_name=file_path, start=offset, end=len(chunk) + offset,
                    content=chunk, typee="text")
            res.append(obj)

            offset += len(chunk)
            chunk = line

    if chunk.strip():
        obj = Chunk(file_name=file_path, start=offset, end=len(chunk) + offset,
                            content=chunk, typee="text")
        res.append(obj)

    return res



def offset_lines(lst):
    res = [0]
    for ele in lst:
        res.append(res[-1] + len(ele) + 1)

    return res


def chunking_code(path, content):

    tree = ast.parse(content)
    top_nodes = []

    for node in ast.iter_child_nodes(tree):
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            top_nodes.append(node)

    lines = content.split("\n")
    offsets = offset_lines(lines)

    

    

    





def chunking_data(repo_path):
    docm_ex = ["txt", "md"]
    code_ex = ["py"]

    res = []

    if not os.path.exists(repo_path):
        print("Error")
        return []

    for root, folder, files in os.walk(repo_path):
        for file in files:
            try:
                current_extention = file.split(".")[1]
            except Exception:
                continue

            if current_extention in docm_ex:
                full_path = os.path.join(root, file)
                with open(full_path, "r") as f:
                    content = f.read()
                    lst = chunking_docs(full_path, content)
                    res.extend(lst)

            if current_extention in code_ex:
                full_path = os.path.join(root, file)
                with open(full_path, "r") as f:
                    content = f.read()
                    lst = chunking_code(full_path, content)
                    # res.extend(lst)


    return res




            



r = chunking_data("/home/hamza-el-achhab/Desktop/rcd/vllm-0.10.1")

# for c in r:
#     print(c.content)
#     print("*"*30)
#     print(len(c.content))
#     print("*"*30)
