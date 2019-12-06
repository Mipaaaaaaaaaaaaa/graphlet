import re
import json
import subprocess
import os
import functools
import numpy as np
from sklearn.decomposition import PCA


#   根据需要初始化变量名
#   graph_name 为该算法中间变量文件名，可修改获得多份数据
#   recept_name 为接收图文件名，用于前端发送 
#   return_name 为返回图文件名，用于前端接收
graph_name = "mylist"
recept_name = "graph_data.json"
return_name = "graph_return.json"

#   根据基础文件名获得其他文件名
write_name = graph_name + ".txt"
result_name = "./Results/UNDIR_RESULTS_" + graph_name + ".arff"

edge_number = 0
vertex_number = 0

try:
    #   读取本地json文件
    load_f = open(recept_name,'r')
    #   创建写入文件
    write_f = open(write_name,"w")
    #   读取json格式
    load_dict = json.load(load_f)
    #   遍历图的边情况，输出至RAGE.exe需要的格式
    edge_number = len(load_dict["graph"]["vertex"])
    vertex_number = len(load_dict["graph"]["edge"])
    for edge in load_dict["graph"]["edge"]:
        mystr = str(edge["source"]) + " " + str(edge["target"]) + "\n"
        write_f.write(mystr)
    write_f.close()
except IOError:
    print("文件graph_data.json不存在" )

#   通过RAGE.exe得到所需多维内容
os.system(r'.\RAGE.exe ' + write_name + " \n")

#   数组的排序函数
def cmp(a,b):
    if int(a["id"]) < int(b["id"]):
        return -1
    else:
        return 1

try:
    #   打开处理好的文件
    fp = open(result_name,"r")
    content = fp.read()
    fp.close()
    pos = content.find("@DATA")
    data = content[pos+6:]
    edges = data.split("\n")
    #   逐行读取
    list = []
    number = []
    for i in edges:
        line = i.split(",")
        temp = []
        count = 0
        for k in line:
            if count != 0 :
                if str.isdigit(k):
                    temp.append(k)
            else:
                if str.isdigit(k):
                    #   获得该行的id
                    number.append(k)
            count = count + 1
        if( len(temp) != 0 ):
            list.append(temp)
    #   降维
    estimator = PCA(n_components=2)
    X_pca = estimator.fit_transform(list)
    #   数组转列表
    mylist = np.mat(X_pca).tolist()
    index = 0
    write_obj = []
    #   逐个转列表
    for i in mylist:
        temp = {}
        temp["id"] = number[index]
        temp["value"] = i
        index = index + 1
        write_obj.append(temp)
    #   排序
    write_obj.sort(key=functools.cmp_to_key(cmp))

    try:
        #   写回
        file_write = open(return_name,'w')
        json.dump(write_obj,file_write,indent=4)
        file_write.close()

    except IOError:    
        print("文件%s无法写入" % return_name )

except IOError:
    print("文件%s不存在" % result_name )