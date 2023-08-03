import requests
import json
import pandas as pd
import time
from bs4 import BeautifulSoup
import re
import os
from selenium import webdriver

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


def Iqiyi(name, content_id,last_id='&'):
    '''

    :param last_id:评论的最后一个id在接口请求中能够看到
    :param pinglun_data: 存放数据的list
    :return: 无return值 保存为一个csv文件
    '''
    pinglun_data = []
    while len(pinglun_data) < 800:
        time.sleep(0.5)
        headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Edg/115.0.1901.183"}
        sort=["TIMEDESC","HOT"]
        url =f"https://sns-comment.iqiyi.com/v3/comment/get_baseline_comments.action?agent_type=118&agent_version=9.11.5&authcookie=null&business_type=17&channel_id=2&content_id={content_id}&last_id={last_id}&need_vote=1&page=NaN&page_size=40&qyid=e5debc58fe819b25ca6de2fe991d92cc&sort=HOT&tail_num=1&callback=jsonp_1690948653064_72360"
        print(url)
        Iqiyi_get = requests.get(url, headers=headers)
        # 获取的数据被js外边包了一个壳 需要对数据进行处理后才能被json.loads解析
        u1 = '{'+Iqiyi_get.text.lstrip('try{ jsonp_16904544092779_86397(').rstrip('}) }catch(e){};')+'}}' #删除获取json的外壳
        # 这个壳我研究了很长时间 死活都没办法被json解析 后来我发现居然是因为我删除的时候多删除了一个括号MMP
        comment_cont = json.loads(u1.encode("utf-8"))["data"]["totalCount"]
        json_data = json.loads(u1.encode("utf-8"))["data"]["comments"]
        for comment in json_data:
            print(comment["id"])
            if 'content' in comment.keys():
                pinglun_data.append([comment['content'],comment["userInfo"]["uname"]])
            #更新last_id
            last_id = comment["id"]
        print(len(pinglun_data))
        if comment_cont-10 <= len(pinglun_data):
            pd.DataFrame(pinglun_data).to_csv(f"./评论CSV/{name}.csv", mode="w")
            pinglun_data.clear()
            break


    else:
        pd.DataFrame(pinglun_data).to_csv(f"./评论CSV/{name}.csv", mode="w")
        pinglun_data.clear()
        return
    # 保存为csv


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
                data_list = [comment["title"], comment["description"], comment["tag"], comment["showDate"],
                             [i["name"] for i in comment['creator']], [i["name"] for i in comment["contributor"]]
                            , comment["page_url"], comment["image_url_normal"], comment["time_length"], comment["hot_score"], comment["tv_id"]]
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
            picture_resp = requests.get(name[-4])
            with open(f"./爱奇艺数据/电视剧海报/{name[0]}.jpg", mode='wb') as f:
                f.write(picture_resp.content)
        df = pd.DataFrame(alldata_list, columns=["title","description","tag","showDate", 'creators', "contributor", "page_url", "img_url", "time_length", "hot_score", "content_id"])
        df.to_csv("./爱奇艺数据/爱奇艺热播.csv")
        return alldata_list


def comment_data_get(path):
    df = pd.read_csv(path)
    for title, content_id in df.iterrows():
        Iqiyi(content_id[1], content_id[-1])


def youku():
    TV_Data = []
    driver = webdriver.Chrome(executable_path="./chromedriver.exe")
    driver.get("https://www.youku.com/channel/webtv/list?filter=type_%E7%94%B5%E8%A7%86%E5%89%A7_year_2023&spm=a2hja.14919748_WEBTV_JINGXUAN.drawer3.d_sort_1")
    css_selectors = ["#app > div.app_normal.window > div.modulelist_s_body > div.videolist_s_body > div > div > div:nth-child(4) > div > div:nth-child({}) > div > div > div.categorypack_info_list > div.categorypack_title.categorypack_short_title > a".format(str(i)) for i in range(41)]
    for css_selector in css_selectors:
        if css_selector == "#app > div.app_normal.window > div.modulelist_s_body > div.videolist_s_body > div > div > div:nth-child(4) > div > div:nth-child(0) > div > div > div.categorypack_info_list > div.categorypack_title.categorypack_short_title > a":
            pass
        else:
            time.sleep(1)
            title = driver.find_element_by_css_selector(css_selector)
            titles = title.get_attribute('title')
            url = (title.get_attribute('href'))
            options = webdriver.ChromeOptions()
            options.add_argument('--disable-blink-features=AutomationControlled')
            driver = webdriver.Chrome(options = options)
            driver.get(url)
            type = driver.find_element_by_css_selector("#app > div > div.play-top-container-new > div.l-container-new > div > div > div.listbox-new > div.right-wrap > div.contents-wrap.contentsNode > div.new-title-wrap > div.new-title-feature > span:nth-child(3)")
            comment = driver.find_element_by_css_selector("#tabsNode > p:nth-child(2) > span")
            fav = driver.find_element_by_css_selector("#app > div > div.play-top-container-new > div.l-container-new > div > div > div.play-paction-wrap-new > div.nav-mamu-new > ul > li.play-fn-li.fn-dianzan > a > span.fav-text")
            collect = driver.find_element_by_css_selector("#app > div > div.play-top-container-new > div.l-container-new > div > div > div.play-paction-wrap-new > div.nav-mamu-new > ul > li.play-fn-li.fn-shoucang > a > span.fav-text")
            intro = driver.find_element_by_css_selector("#app > div > div.play-top-container-new > div.l-container-new > div > div > div.listbox-new > div.right-wrap > div.contents-wrap.contentsNode > div.new-title-wrap > div.new-title-feature > p")
            driver.execute_script("arguments[0].click();", intro)
            introduction = driver.find_element_by_css_selector("#app > div > div.play-top-container-new > div.l-container-new > div > div > div.listbox-new > div.right-wrap > div.new-intro-wrap > div > div.new-intro-detail > div:nth-child(2)")
            TV_Data.append([titles,type,comment, fav, collect,introduction])
            print(TV_Data)
    pd.DataFrame(TV_Data).to_csv("./youku_data.csv")



if __name__ == "__main__":
    # dorama_url_get()
    # TXvideourl_get()
    # dorama_url_get()
    # Iqiyi("测试","1116314049607400")
    # dorama_data_get()
    comment_data_get("./爱奇艺数据/爱奇艺热播.csv")

