import requests
import json
import pandas as pd
import time
from bs4 import BeautifulSoup
import re
import os

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Edg/115.0.1901.183'}


def mkdir(path):
    '''
    :param path:文件夹路径 会自动递归生成文件夹
    :return: 无返回值
    '''
    # os.path.exists 函数判断文件夹是否存在
    folder = os.path.exists(path)

    # 判断是否存在文件夹如果不存在则创建为文件夹
    if not folder:
        # os.makedirs 传入一个path路径，生成一个递归的文件夹；如果文件夹存在，就会报错,因此创建文件夹之前，需要使用os.path.exists(path)函数判断文件夹是否存在；
        os.makedirs(path)  # makedirs 创建文件时如果路径不存在会创建这个路径
        print('文件夹创建成功：', path)

    else:
        print('文件夹已经存在：', path)


def get_danmu():
    '''
    :return: 将弹幕保存一个csv文件
    '''
    danmu_data = []
    for i in range(0, 600000+30000, 30000):
        url = f'https://dm.video.qq.com/barrage/segment/t0046qdufmw/t/v1/{i}/{i+30000}'
        data = {'timestamp':i}
        res = requests.get(url, params=data, headers=headers)
        # 转为json对象
        json_data = json.loads(res.text)['barrage_list']
        # 遍历comments中的弹幕信息
        for comment in json_data:
            danmu_data.append(comment['content'])
    save_csv = pd.DataFrame(data=danmu_data)
    # print(save_csv.head())
    #保存为csv
    save_csv.to_csv(path_or_buf="./test.csv", encoding="utf_8_sig")
    time.sleep(2)


def dorama_url_get():
    url = "https://v.qq.com/channel/tv/list?filter_params=ifeature%3D-1%26iarea%3D-1%26iyear%3D2023%26ipay%3D-1%26sort%3D75&page_id=channel_list_second_page"
    dorama_url = requests.get(url=url,headers=headers)
    dorama_text = dorama_url.text
    print(dorama_url.text)
    bs = BeautifulSoup(dorama_text,"html.parser")
    a = bs.select("card-list-wrap a")
    print(a)


pinglun_data = []


def Iqiyi(last_id, pinglun_data):
    '''

    :param last_id:评论的最后一个id在接口请求中能够看到
    :param pinglun_data: 存放数据的list
    :return: 无return值 保存为一个csv文件
    '''

    headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Edg/115.0.1901.183"}
    url =f"https://sns-comment.iqiyi.com/v3/comment/get_baseline_comments.action?agent_type=118&agent_version=9.11.5&authcookie=null&business_type=17&channel_id=2&content_id=7967612554814600&last_id={last_id}&need_vote=1&page=NaN&page_size=40&qyid=e5debc58fe819b25ca6de2fe991d92cc&sort=HOT&tail_num=1&callback=jsonp_1690506592425_29304"
    Iqiyi_get = requests.get(url,headers=headers)
    # 获取的数据被js外边包了一个壳 需要对数据进行处理后才能被json.loads解析
    u1 = '{'+Iqiyi_get.text.lstrip('try{ jsonp_16904544092779_86397(').rstrip('}) }catch(e){};')+'}}' #删除获取json的外壳
    # 这个壳我研究了很长时间 死活都没办法被json解析 后来我发现居然是因为我删除的时候多删除了一个括号MMP
    json_data = json.loads(u1.encode("utf-8"))["data"]["comments"]
    for comment in json_data:
        print(comment["id"])
        if 'content' in comment.keys():
            pinglun_data.append(comment['content'])
        #更新last_id
        last_id = comment['id']
    print(len(pinglun_data))


    if len(pinglun_data) < 700 :
        time.sleep(0.5)
        Iqiyi(last_id, pinglun_data)
        # 递归

    else:
        return
    # 保存为csv
    df = pd.DataFrame(pinglun_data)
    df.to_csv('./pinglun.csv')


def dorama_data_get():
    '''
    :return: 存放有所有电视剧名称，简介，标签，日期，导演，演员，电视剧地址，电视剧海报地址的List
    '''
    alldata_list = []
    try:
        for i in range(1,5):
            headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Edg/115.0.1901.183"}
            url = f"https://mesh.if.iqiyi.com/portal/videolib/pcw/data?version=1.0&ret_num=30&page_id={i}&device_id=e5debc58fe819b25ca6de2fe991d92cc&passport_id=&watch_list=7967612554814600,2739,1005&recent_selected_tag=2023&recent_search_query=&ip=202.108.14.240&scale=150&channel_id=2&tagName=&market_release_date_level=2023&mode=24"
            data = requests.get(url=url,headers=headers)
            json_data = json.loads(data.text)["data"]
            for comment in json_data:
                data_list = [comment["title"], comment["description"], comment["tag"], comment["showDate"],[i["name"] for i in comment['creator']], [i["name"] for i in comment["contributor"]],comment["page_url"],comment["image_url_normal"]]
                print(comment["page_url"])
                print(comment["image_url_normal"])
                print(data_list)
                alldata_list.append(data_list)
                time.sleep(0.5)
                ## 这里是尝试使用接口获取数据,但是爱奇艺的接口被加密过,我没有办法自动获取接口进行爬取搁置在此

                # dorama_data = requests.get(comment["page_url"], headers=headers).text
                # entity_id = comment["firstId"]
                # data_url = f"https://mesh.if.iqiyi.com/tvg/pcw/base_info?entity_id={entity_id}&timestamp=1690514642425&src=pcw_tvg&vip_status=0&vip_type=&auth_cookie=&device_id=e5debc58fe819b25ca6de2fe991d92cc&user_id=&app_version=5.0.0&scale=148&sign=A2313B80BB73DF0F8238321D05E43B39"
                # dorama_data = requests.get(data_url, headers=headers).text
                # comment_json_data = json.loads(dorama_data)["data"]
                # data_list.append(comment_json_data["base_data"]["score_info"]["sns_score"])
                # comment_get_url = f"https://sns-comment.iqiyi.com/v3/comment/get_bulk_count_data.action?extend_business_type=13&content_ids={i}&qsRequestId=commentCount&callback=jsonp_3"
                # json_text = requests.get(url=comment_get_url,headers=headers).text
                #
                # json_text = '{'+json_text.lstrip("try{ jsonp_3(").rstrip('}) }catch(e){};')+'}'
                # print(json_text)
                # comment_count = json.loads(json_text)["data"]
                # for count in comment_count:
                #     data_list.append(count["commentCount"])
                # print(data_list)

    except:
        mkdir("./爱奇艺数据/电视剧海报")
        for name in alldata_list:
            picture_resp = requests.get(name[-1])
            with open(f"./爱奇艺数据/电视剧海报/{name[0]}.jpg", mode='wb') as f:
                f.write(picture_resp.content)
        df = pd.DataFrame(alldata_list, columns=["title","description","tag","showDate", 'creators', "contributor", "page_url","img_url"])
        df.to_csv("./爱奇艺数据/爱奇艺热播.csv")
        return alldata_list
def TXvideourl_get():
    url = "https://youku.com/channel/webtv/list?filter=type_%E7%94%B5%E8%A7%86%E5%89%A7_year_2023&spm=a2hja.14919748_WEBTV_JINGXUAN.drawer3.d_main_area_1"
    # headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Edg/115.0.1901.183', "Cookie":"pgv_pvid=184197000; RK=S20sAhgAH/; ptcz=77015465c8b1c3cf6c05b8fd49727f783a61aca766fa4ffaf42994df2f8236d8; pac_uid=1_1214602074; iip=0; eas_sid=a1X6I9n0F1U1w041v3s6K6r9C1; qq_domain_video_guid_verify=4cccd06f254eab04; video_platform=2; video_guid=4cccd06f254eab04; pgv_info=ssid=s5322851164; o_cookie=1214602074; vversion_name=8.2.95; video_omgid=4cccd06f254eab04; _video_qq_login_time_init=1690377511; qz_gdt=seq4czadaaaimuaejdja; login_time_last=2023-7-26 21:37:26"}
    data = requests.get(url=url, headers=headers).text
    obj = re.compile(r'<div class="videolist_container_inner">.*?<a class="aplus_exp aplus_clk" herf="(?P<url>.*?)"title="(?P<name>.*?)"target=.*?<img s' 
                     r'rc="(?P<img_url>.*?)"',re.S)
    res = obj.finditer(data)
    for i in res:
        print(i)






if __name__ == "__main__":
    dorama_data_get()
    # TXvideourl_get()
    # dorama_url_get()
    # Iqiyi("4620174475752421", pinglun_data)



