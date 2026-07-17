import ast
from pydantic import BaseModel
import os
import sys



class Chunk(BaseModel):
    file_name: str
    start: int
    end: int
    content: str
    type: str




def chunk_text(file_path, content):
    res = []
    chunk = ""
    st = 0

    if len(content) <= 2000:
        return [Chunk(file_name=file_path, start=0, end=len(content), content=content)]
    


    lines = content.split()

    # for line in lines:
    #     line += "\n"
    #     if len(line) + len(chunk) < 2000:
    #         chunk += line
        
    #     else:
    #         obj = Chunk(file_name=file_path, start=st, end=st+len(chunk), type="text")
    #         res.append(obj)
    #         st += len(chunk)
    #         chunk = line
    

    return res



        





def chunking_data(file_path):

    res: list[Chunk] = []

    for root, _, files in os.walk(file_path):
        for file in files:
            try:
                ext = file.split(".")[1]
            except Exception:
                continue
            if ext in {"txt", "md"}:
                full_path = os.path.join(root, file)

                with open(full_path, "r") as f:
                    data = f.read()
                lst = chunk_text(full_path, data)
                res.extend(lst)


    return res






res = chunking_data("/home/hel-achh/goinfre/rcd/vllm-0.10.1")


