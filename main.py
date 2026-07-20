

import ast
import os
import sys
import re
from pydantic import BaseModel
from tqdm import tqdm
from rank_bm25 import BM25Okapi
import pickle
import json
import numpy
from transformers import AutoTokenizer, AutoModelForCausalLM



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
    res = []

    tree = ast.parse(content)
    top_nodes = []

    for node in ast.iter_child_nodes(tree):
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            top_nodes.append(node)

    lines = content.split("\n")
    offsets = offset_lines(lines)

    for node in top_nodes:
        start_line = node.lineno - 1
        end_line = node.end_lineno

        start_indx = offsets[start_line]
        end_indx = offsets[end_line]

        data = content[start_indx:end_indx]

        obj = Chunk(file_name=path, start=start_indx, end=end_indx, content=data, typee="code")
        res.append(obj)

    return res


    

    





def chunking_data(repo_path):
    docm_ex = ["txt", "md"]
    code_ex = ["py"]

    res = []

    if not os.path.exists(repo_path):
        print("Error")
        return []

    for root, folder, files in tqdm(os.walk(repo_path), desc="fd"):
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
                    res.extend(lst)


    return res




def tokenizer(text):
    text = text.lower()
    return text.split(" ")


def build_bm_obj_and_list(chunks):
    matrix = []

    for obj in tqdm(chunks, desc="building"):
        matrix.append(tokenizer(obj.content))

    bm25_obj = BM25Okapi(matrix)
    binarries = pickle.dumps(bm25_obj)
    with open("BM25.pkl", "wb") as f:
        f.write(binarries)

    data = []
    for obj in chunks:
        data.append(obj.model_dump())
    with open("chunks.json", "w") as f:
        f.write(json.dumps(data, indent=2))

    print("BM25 and CHUNK lists are saved.")



def load_bm25_obj():
    with open("/home/hel-achh/goinfre/rcd/BM25.pkl", "rb") as f:
        data = f.read()
        bm25_o = pickle.loads(data)

    with open("/home/hel-achh/goinfre/rcd/chunks.json", "r") as f:
        data = f.read()
        lst_of_objs = json.loads(data)

    return bm25_o, lst_of_objs

    
def retrive(query, bm25, lst, k):
    query_tokened = tokenizer(query)

    scores = bm25.get_scores(query_tokened)
    best_k_indexes = numpy.argsort(scores)[::-1][:k]

    res = []
    for idx in best_k_indexes:
        res.append(lst[idx])

    return res



def merge_data(lst):
    res = ""
    for dct in lst:
        res += dct["content"]
        res += "\n"    
    return res




def generate_answer(fully_prompt, max_new=60) -> str:
    
    TOKENIZER = AutoTokenizer.from_pretrained("Qwen/Qwen3-0.6B")
    MODEL_OBJ = AutoModelForCausalLM.from_pretrained("Qwen/Qwen3-0.6B")

    inputs = TOKENIZER(fully_prompt, return_tensors="pt")
    outputs = MODEL_OBJ.generate(**inputs, max_new_tokens=max_new)

    length_of_prompt = len(inputs['input_ids'][0].tolist())
    ids = (outputs[0].tolist())
    ids = ids[length_of_prompt:]

    answer = TOKENIZER.decode(ids)
    return answer







question = "What are the default values for FP8_MIN and FP8_MAX constants in vLLM's triton_flash_attention module?"


build_bm_obj_and_list(chunking_data("/home/hel-achh/goinfre/rcd/vllm-0.10.1"))
bm25, list_ob_objs = load_bm25_obj()
retrived_data = retrive(question, bm25, list_ob_objs, 5)
merged_data = merge_data(retrived_data)


fully_prompt = f"""
the content is :
{merged_data}

base on these privouse data answer on this question

QUESTION: {question}

ANSWER:

"""

answer = generate_answer(fully_prompt)
print(answer)
