import csv
from wordcloud import WordCloud
import jieba
from PIL import Image  # 安装词云的时候一起装上的
import numpy as np # 安装词云的时候一起装上的
import os

# 设置停用词表
stopwords = set()
content = [line.strip() for line in open('cn_stopwords.txt', 'r',encoding="utf-8").readlines()]
stopwords.update(content)

# 读取影评，返回影评列表

def readComment(name):
    with open(f"./评论CSV/{name}.csv", 'r',encoding="utf-8") as file:
        csvRead = csv.reader(file) #加载文件数据
        return [item[1] for item in csvRead] #这是一个列表生成式
        #生成的item应该是一个二维列表。item[2]则表示item的第二列元素
        #返回值是一个列表，列表元素是影评的内容
# 生成词云图

def generateWordCloud(name):
    commentlist = readComment(name) #获取影评内容
    finalComment = ""
    for comment in commentlist:
        finalComment += comment  #把所有影评拼接成一个字符串

    # 读取轮廓图片,并且处理为ndarray的格式（numpy）
    image = np.array(Image.open('./0.jpg'))  # 0.jpg 必须是一个白底图片，且图片内容不能有白色
    # 使用了image属性，词云会生成为所选用图片轮廓的形状
    # 词云的属性
    wordCloud = WordCloud(
        width = 1200,  #词云的高度
        height = 600, #词云的宽度
        font_path = "STLITI.TTF", # 字体路径  在C:\Windows\Fonts目录下找一个中文样式的字体复制到工作目录
        background_color = "white", # 背景颜色
        mask = image,  # 图片的轮廓 #可选属性，不选择默认是矩形词云
        stopwords=stopwords).generate(" ".join(jieba.cut(finalComment)))  #jieba.cut(finalComment)) :把影评的字符串切割成词语  generate：把词语组成词云
    # 生成词云文件
    wordCloud.to_file(f'./词云/{name}.png')


def get_file_name(path):
    file_dir = path
    files = os.listdir(file_dir)
    return files


if __name__ == '__main__':
    path = "D:\数据分析项目\评论CSV"
    a = get_file_name(path)
    for i in a:
        generateWordCloud(i[:-4])
