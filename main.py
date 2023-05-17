import asyncio
import httpx
from bs4 import BeautifulSoup
import re
import aiomysql
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# For A1-----------------------------------------------
# For A1-----------------------------------------------
# For A1-----------------------------------------------
# For A1-----------------------------------------------

db_Doing = False

async def fetch_url(url):
    """
    非同步獲取網址的函數。

    參數：
    url -- 要獲取的網址

    返回值：
    獲取的網頁內容

    使用非同步方式向指定的網址發送請求，獲取網頁的內容並返回。

    """
    # async with httpx.AsyncClient() as client:
    #     headers = {
    #         'accept-encoding': 'gzip, deflate, br',
    #         'accept-language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
    #         'cookie': 'session-id=257-2028996-0896043; i18n-prefs=EGP; lc-acbeg=en_AE; ubid-acbeg=261-1798037-1499267; session-id-time=2082787201l; session-token=lTKhbG4Udz66QrWRIjnEK1rIGOjJh7oHQ7qE3DU++H+8t6b7fxWe7YXQDdfytAXhKxVYVbpH4W/vYUzyCFw/e1/pQAUxgBjoHHrhcgxGm4Nn4rPOOw+IlnX4THjoXO7vaIR21GNvriFz6J3iovRnI6ie9jyHr/q0ZgnUoVF01ymSiKG98Rs9hSNn830FeGM3yGtxBQ0YMJEmWYuT6waUwIhl+GzhqyXEK9/DGQDGokQ=; csm-hit=tb:s-N7M0X2V9YV3G1AWZ7ZX4|1684168857815&t:1684168858301&adb:adblk_yes',
    #         'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
    #         'Origin':'https://www.amazon.eg'
    #     }
    #     response = await client.get(url, headers=headers)

        # 非必要不使用 selenium , 效能問題
        # webdriver_path = '/path/to/chromedriver'
        #
        # # 设置 Chrome 选项
        # chrome_options = Options()
        # chrome_options.add_argument('--headless')  # 无界面模式
        #
        # # 创建 Chrome WebDriver
        # driver = webdriver.Chrome(service=Service(webdriver_path), options=chrome_options)
        #
        # # 打开目标网页
        # driver.get(url)
        #
        # # 等待页面加载
        # driver.implicitly_wait(2)
        #
        # # 设置请求头
        # for key, value in headers.items():
        #     driver.execute_cdp_cmd("Network.setExtraHTTPHeaders", {"headers": {key: value}})
        #
        # # 获取网页的HTML源代码
        # html = driver.page_source
        # driver.quit()

    async with httpx.AsyncClient(http2=True, limits=httpx.Limits(max_connections=10)) as client:
        headers = httpx.Headers({
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'cookie': 'session-id=257-2028996-0896043; i18n-prefs=EGP; lc-acbeg=en_AE; ubid-acbeg=261-1798037-1499267; session-id-time=2082787201l; session-token=lTKhbG4Udz66QrWRIjnEK1rIGOjJh7oHQ7qE3DU++H+8t6b7fxWe7YXQDdfytAXhKxVYVbpH4W/vYUzyCFw/e1/pQAUxgBjoHHrhcgxGm4Nn4rPOOw+IlnX4THjoXO7vaIR21GNvriFz6J3iovRnI6ie9jyHr/q0ZgnUoVF01ymSiKG98Rs9hSNn830FeGM3yGtxBQ0YMJEmWYuT6waUwIhl+GzhqyXEK9/DGQDGokQ=; csm-hit=tb:s-N7M0X2V9YV3G1AWZ7ZX4|1684168857815&t:1684168858301&adb:adblk_yes',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
            'Origin': 'https://www.amazon.eg'
        })
        response = await client.get(url, headers=headers)
        return response.text

async def excute_async(sql, values):
    """
    執行非同步 SQL 語句的函數。

    參數：
    sql -- SQL 語句
    values -- 語句中的參數值

    返回值：
    返回受影響的資料行數

    建立與資料庫的連線，執行 SQL 語句並取得受影響的資料行數。最後提交變更並關閉連線。

    """
    # 建立與資料庫的連線
    conn = await aiomysql.connect(
        host="localhost",
        port=3306,
        user="root",
        password="J2294140319",
        db="woshop_db"
    )

    # 建立游標
    cur = await conn.cursor()

    # 執行 SQL query 語句
    sql = sql
    values = values
    result = await cur.execute(sql, values)
    # 提交變更
    await conn.commit()
    # 關閉游標與連線
    await cur.close()
    return result

async def query_async(sql, values):
    """
    執行非同步查詢的函數。

    參數：
    sql -- SQL 查詢語句
    values -- 查詢的參數值

    返回值：
    返回查詢結果的元組

    建立與資料庫的連線，執行 SQL 查詢，並取得查詢結果的元組。最後提交變更並關閉連線。

    """
    # 建立與資料庫的連線
    conn = await aiomysql.connect(
        host="localhost",
        port=3306,
        user="root",
        password="J2294140319",
        db="woshop_db"
    )

    # 建立游標
    cur = await conn.cursor()

    # 執行 SQL INSERT 語句
    sql = sql
    values = values
    await cur.execute(sql, values)
    # 取得查詢結果
    results = await cur.fetchall()

    # 提交變更
    await conn.commit()
    # 關閉游標與連線
    await cur.close()
    return results

async def add_newdata_to_goodslan(goods_id ,goods_name):
    """
    將新資料添加到 sp_goods_lang_ 表中的函數。

    參數：
    goods_id -- 商品ID
    goods_name -- 商品名稱

    返回值：
    如果商品已存在於 sp_goods_lang_ 表中，則返回相應的訊息；否則返回 SQL 語句。

    首先，檢查商品是否已存在於 sp_goods_lang_ 表中，如果是，則返回已有資料的訊息。
    否則，生成 SQL 語句並返回以添加新資料。

    """
    if not db_Doing:
        return "DB處理關閉中"
    langcode_array = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 18]
    sql = "select count(1) from sp_goods_lang where goods_id=%s and goods_name=%s LIMIT 1"
    result = await query_async(sql, (goods_id, goods_name))
    sql = ""
    if int(result[0][0]) > 0:
        msg = str(goods_id) + ":品項:" + goods_name + "已有資料再sp_goods_lang_"
        print(msg)
        return msg
    result_count = 0
    for langcode in langcode_array:
        sql = ("INSERT INTO `sp_goods_lang` (`goods_id`, `lang_id`, `goods_name`, `goods_desc`) VALUES (%s, {lang_id}, %s, NULL);").replace("{lang_id}", str(langcode))
        result_count += await excute_async(sql, (goods_id, goods_name))


    return result_count

async def add_newdata_to_sp_goods_pic_(goods_id, img_url, sort):
    """
    將新資料添加到 sp_goods_pic_ 表中的函數。

    參數：
    goods_id -- 商品ID
    img_url -- 圖片網址
    sort    -- 排序

    返回值：
    如果商品已存在於 sp_goods_pic_ 表中，則返回相應的訊息；否則返回 SQL 語句。

    首先，檢查商品是否已存在於 sp_goods_pic_ 表中，如果是，則返回已有資料的訊息。
    否則，生成 SQL 語句並返回以添加新資料。

    """
    if not db_Doing:
        return "DB處理關閉中"
    sql = "select count(1) from sp_goods_pic where goods_id=%s and img_url=%s  LIMIT 1"
    result = await query_async(sql, (goods_id, img_url))
    sql = ""
    if int(result[0][0]) > 0:
        msg = str(goods_id) + ":圖片:" + img_url + "已有資料再sp_goods_pic_"
        print(msg)
        return msg
    result_count = 0
    sql = "INSERT INTO `sp_goods_pic` (`goods_id`, `img_url`, `sort`) VALUES (%s, %s, %s);"
    result_count = await excute_async(sql, (goods_id, img_url, sort))


    return result_count


async def add_newdata_to_sp_goods_(goods_id, goods_name, thumb_url, market_price, shop_price, cate_id, goods_desc):
    """
    將新資料添加到 sp_goods_表中的函數。

    參數：
    goods_id -- 商品ID
    img_url -- 圖片網址
    sort    -- 排序

    返回值：
    如果商品已存在於 sp_goods_pic 表中，則返回相應的訊息；否則返回 SQL 語句。

    首先，檢查商品是否已存在於 sp_goods_pic_ 表中，如果是，則返回已有資料的訊息。
    否則，生成 SQL 語句並返回以添加新資料。

    """
    if not db_Doing:
        return "DB處理關閉中"
    sql = "select count(1) from sp_goods where id=%s and goods_name=%s  LIMIT 1"
    result = await query_async(sql, (goods_id, goods_name))
    sql = ""
    if int(result[0][0]) > 0:
        msg = str(goods_id) + "商品名稱:" + goods_name + "已有資料再sp_goods_"
        print(msg)
        return msg
    result_count = 0
    sql = "INSERT INTO `sp_goods` " \
          "(`id`, `goods_name`, `search_keywords`, `thumb_url`, " \
          "`market_price`, `shop_price`, `min_market_price`, `max_market_price`," \
          "`cate_id`, `goods_desc`, `keywords`, `goods_brief`," \
          "`addtime`, `leixing`, `shop_id`,`total`," \
          " `min_price`, `max_price`) " \
          "VALUES (%s, %s, %s, %s, " \
          "%s, %s, %s, %s," \
          "%s, %s, %s, %s," \
          "%s, %s, %s, %s," \
          "%s, %s);"
    timestamp = int(time.time())
    result_count = await excute_async(sql, (goods_id, goods_name, goods_name, thumb_url,
                                            market_price, shop_price, market_price, market_price,
                                            cate_id, goods_desc, goods_name, goods_name,
                                            timestamp, 1, 1, 9999,
                                            shop_price, shop_price))

    return result_count

async def add_newdata_to_sp_category_(cat_id, cat_name,parent_id,sort):
    """
    將新資料添加到 sp_category_表中的函數。

    參數：
    goods_id -- 商品ID
    img_url -- 圖片網址
    sort    -- 排序

    返回值：
    如果商品已存在於 sp_category_ 表中，則返回相應的訊息；否則返回 SQL 語句。

    首先，檢查商品是否已存在於 sp_goods_pic_ 表中，如果是，則返回已有資料的訊息。
    否則，生成 SQL 語句並返回以添加新資料。

    """
    if not db_Doing:
        return "DB處理關閉中"
    sql = "select count(1) from sp_category where id=%s LIMIT 1"
    result = await query_async(sql, cat_id)
    sql = ""
    if int(result[0][0]) > 0:
        msg = cat_id + "商品名稱:" + cat_name + "已有資料再sp_category_"
        print(msg)
        return msg
    result_count = 0
    sql = "INSERT INTO `sp_category` (" \
          "`id`, `cate_name`,`cate_desc`, `search_keywords`," \
          " `keywords`, `pid`, `sort`) " \
          "VALUES " \
          "(%s,%s ,%s,%s , " \
          "%s,%s,%s);"
    result_count = await excute_async(sql, (cat_id, cat_name, cat_name, cat_name,
                                            cat_name, parent_id, sort))

    return result_count

async def product_list_web_crawler(url, start_id,cat_id):
    """
    解析商品頁面的非同步函數。
    根據給定的URL和起始ID，獲取商品頁面的相關數據，包括商品名稱、價格、圖片等。

    Args:
        url (str): 商品頁面的URL。
        start_id (int): 起始ID。

    Returns:
        None

    """
    # 變數初始化
    id_array = []
    productnames_array = []
    price_array = []
    marketprice_array = []
    product_pics = []
    product_piccount = []
    product_desc = []
    thumb_img_array = []
    skipItem=[]
    if url == '':
        print(cat_id)
        print('網址異常')
        return cat_id

    html = await fetch_url(url)
    soup = BeautifulSoup(html, 'html.parser')
    if "cs_503_link" in html:
        print("伺服器錯誤")
        print(cat_id)
        return cat_id
    # 解析網頁，獲取商品名稱和價格
    # === 商品名稱 ===
    product_names = soup.select('.a-size-base-plus')
    for product_name in product_names:
        productnames_array.append(product_name.text.strip())
        print(product_name.text.strip())
        id_array.append(start_id)
        start_id += 1

    # === 銷售價格 ===
    items = soup.select('.s-card-container')
    price_elements = soup.select('.a-price .a-offscreen')
    for index, item in enumerate(items, 1):
        price_element = item.select_one('.a-price .a-offscreen')
        if price_element is not None and price_element:
            price = re.sub(r'[^\d.]', '', price_element.text.strip())
        else:
            price = '無價格資訊'
            skipItem.append(index-1)
        price_array.append(price)
    # for price_element in price_elements:
    #     if price_element:
    #         price = re.sub(r'[^\d.]', '', price_element.text.strip())
    #     else:
    #         price = '無價格資訊'


    # === 市場價格 ===
    marketprice_elements = soup.select('a-offscreen')
    for price_index in range(0, len(price_array)):
        if price_index in skipItem:
            marketprice = 0.0
            price_index += 1
        else:
            if price_index < len(marketprice_elements) and marketprice_elements[price_index]:
                marketprice = re.sub(r'[^\d.]', '', marketprice_elements[price_index].text.strip())
            else:
                if isinstance(price_array[price_index], (list, tuple)):  # 檢查元素是否為序列
                    marketprice = [float(element)  * 1.2 for element in price_array[price_index]]
                else:
                    marketprice = float(price_array[price_index]) * 1.2
            price_index += 1
        marketprice_array.append(marketprice)

    # thumb_img
    thumbnail_elements = soup.select('.s-image')
    for thumbnail_element in thumbnail_elements:
        thumbnail_url = thumbnail_element['src']
        thumb_img_array.append(thumbnail_url)

    # 開始處理個別商品頁的資訊
    print("開始", len(productnames_array), '筆品項')

    # 搜尋個別商品頁面，獲取更多商品圖片和描述
    image_urls = []

    # 取得個別商品頁連結(因為有一個商品在列表中有多個連結所以 會有多個資訊)
    item_links = soup.select('.s-product-image-container .a-link-normal ')
    #print("item_links:", len(item_links))
    numitem_link = 0
    print('開始抓圖片起始點', "=>item_links:", len(item_links))
    for item_link in item_links:
        numitem_link += 1
        time.sleep(0.2)
        print("開始抓圖片:", numitem_link)
        pic_count = 0
        if item_link:
            item_url = item_link['href']
            item_url = 'https://www.amazon.eg' + item_url
            item_html = await fetch_url(item_url)
            item_soup = BeautifulSoup(item_html, 'html.parser')
            # print("開始抓圖片:", numitem_link)
            # 獲取商品描述
            #print("開始抓圖片:", numitem_link, '=>商品描述')
            description_element = item_soup.select_one('#productDescription .a-unordered-list')
            description = description_element.text.strip() if description_element else '無商品描述'
            product_desc.append(description)


            # 尋找所有商品圖片的URL
            #print("開始抓圖片:", numitem_link, '=>Url')
            script_tags = item_soup.find_all('script')

            pattern = r"'colorImages': \{.*?'initial': (\[.*?\])\}"
            # 使用正则表达式提取 "large" 属性值
            pattern1 = r'"large"\s*:\s*"([^"]+)"'

            for script_tag in script_tags:
                if "ImageBlockATF" in script_tag.text:
                    match = re.search(pattern, script_tag.text)
                    if match:
                        script_data = match.string
                        matches = re.findall(pattern1, script_data)

                        # 打印提取到的"hiRes"值
                        # 印出所有商品圖片的URL和商品描述
                        for image_url in matches:
                            if image_url not in image_urls and image_url:
                                image_urls.append(image_url)
                                # print(image_url)
                                pic_count += 1
                        product_piccount.append(pic_count)
                        product_pics.append(image_urls)

    # # 將列表轉換為元組，以便在集合中使用
    # tuple_list = [tuple(sub_list) for sub_list in product_pics]
    #
    # # 使用集合來去除重複元組
    # unique_tuples = set(tuple_list)

    # # 將元組轉換回列表
    # unique_product_pics = [list(sub_tuple) for sub_tuple in unique_tuples]
    #print("測試")
    # 印出商品流水號（Id）、商品名稱和價格
    skip = 0
    product_pic_index = 0
    # 因為會有沒價格跳過的調整項
    id_minus = 0
    for num in range(0, len(productnames_array)):
        if num in skipItem:
            id_minus += 1
            continue
        print("第", num + 1, "筆資料")
        print("Id:", id_array[num]-id_minus)
        print("商品名稱:", productnames_array[num])
        print("市場價格:", marketprice_array[num])
        print("銷售價格:", price_array[num])
        print("thumb_img:", thumb_img_array[num])

        # DB填寫
        # goods_lang 填寫
        await add_newdata_to_goodslan(id_array[num]-id_minus, productnames_array[num])

        # DB填寫
        # add_newdata_to_sp_goods_ 填寫
        print("商品描述:", product_desc[num])
        await add_newdata_to_sp_goods_(id_array[num]-id_minus, productnames_array[num], thumb_img_array[num],
                                       marketprice_array[num], price_array[num], cat_id, product_desc[num])
        print("所有商品圖片URL:")
    id_minus = 0
    for picnum in range(0, len(product_piccount)):
        if picnum in skipItem:
            id_minus += 1
            continue
        product_pic_self_index = 0
        for product_pic_count in range(0, product_piccount[picnum]):
            if product_pic_index < len(product_pics[0]):
                # print(product_pic_index, '.:', product_pics[0][product_pic_index])
                # DB填寫
                # add_newdata_to_sp_goods_pic_ 填寫
                await add_newdata_to_sp_goods_pic_(id_array[picnum]-id_minus, product_pics[0][product_pic_index], product_pic_self_index)
                product_pic_index += 1
                product_pic_self_index += 1
    return int(id_array[-1]+1-id_minus)

async def get_categories(url):
    # 设置 WebDriver 的路径
    webdriver_path = '/path/to/chromedriver'

    # 设置 Chrome 选项
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # 无界面模式

    # 创建 Chrome WebDriver
    driver = webdriver.Chrome(service=Service(webdriver_path), options=chrome_options)

    # 打开目标网页
    driver.get(url)
    print(url)
    # 查找类别元素并提取数据
    categories = driver.find_elements(By.CSS_SELECTOR, '#departments .a-unordered-list span span span')

    category_list = []
    for category in categories:
        category_list.append(category.text.strip())

    # 关闭 WebDriver
    driver.quit()
    cat_id = 1
    parent_id = 1
    sort = 1

    await add_newdata_to_sp_category_(cat_id, category_list[0], 0, sort)
    # 打印类别列表
    for category_index in range(1, len(category_list)):
        cat_id += 1
        sort += 1
        await add_newdata_to_sp_category_(cat_id, category_list[category_index], parent_id, sort)
        print(category_list[category_index])
    return categories

async def main():
    """
    主函數的非同步實現。

    該函數是整個程序的入口，用於協調和調用其他非同步函數。
    在主函數內，可以根據具體需求執行一系列的非同步任務，例如發送請求、解析數據等。
    通常，主函數會使用 `await` 關鍵字來等待非同步操作的完成，以確保程序的順序執行。

    """
    # 取列表網址
    # Car & Vehicle Electronics 2
    # url = 'https://www.amazon.eg/s?i=electronics&bbn=18018103031&rh=n%3A18018102031%2Cn%3A21832871031%2Cp_4%3AXO&dc&language=en_AE&ds=v1%3ApMShBZkZzR8pD3oeU5BGDcqS3dNMS7rNcnEEKJWuEGo&pf_rd_i=18018102031&pf_rd_m=A1ZVRGNO5AYLOV&pf_rd_p=825c0142-9b0c-4a77-a6f2-b100f037e545&pf_rd_r=VF466KFA3FWQ7827B7MK&pf_rd_s=mobile-hybrid-12&pf_rd_t=30901&qid=1684165240&rnid=18018103031&ref=sr_nr_n_1'
    ## 第二頁有異常
    # url = 'https://www.amazon.eg/-/en/s?i=electronics&bbn=18018103031&rh=n%3A18018102031%2Cn%3A21832871031%2Cp_4%3AXO&dc&page=2&language=en_AE&pf_rd_i=18018102031&pf_rd_m=A1ZVRGNO5AYLOV&pf_rd_p=825c0142-9b0c-4a77-a6f2-b100f037e545&pf_rd_r=VF466KFA3FWQ7827B7MK&pf_rd_s=mobile-hybrid-12&pf_rd_t=30901&qid=1684165400&rnid=18018103031&ref=sr_pg_2'
    # Computers, Components & Accessories 3
    # 1
    # url = 'https://www.amazon.eg/s?i=electronics&bbn=18018103031&rh=n%3A18018102031%2Cn%3A21832872031%2Cp_4%3AXO&dc&language=en_AE&ds=v1%3AK2LpIMoZ8SUX6GRJjOTM5482WAPrTrpZUomfeLFN6iA&pf_rd_i=18018102031&pf_rd_m=A1ZVRGNO5AYLOV&pf_rd_p=825c0142-9b0c-4a77-a6f2-b100f037e545&pf_rd_r=VF466KFA3FWQ7827B7MK&pf_rd_s=mobile-hybrid-12&pf_rd_t=30901&qid=1684165240&rnid=18018103031&ref=sr_nr_n_2'
    # 2
    #url = 'https://www.amazon.eg/-/en/s?i=electronics&bbn=18018103031&rh=n%3A18018102031%2Cn%3A21832872031%2Cp_4%3AXO&dc&page=2&language=en_AE&pf_rd_i=18018102031&pf_rd_m=A1ZVRGNO5AYLOV&pf_rd_p=825c0142-9b0c-4a77-a6f2-b100f037e545&pf_rd_r=VF466KFA3FWQ7827B7MK&pf_rd_s=mobile-hybrid-12&pf_rd_t=30901&qid=1684167267&rnid=18018103031&ref=sr_pg_2'
    # Hi-Fi & Home Audio 5
    # url = 'https://www.amazon.eg/s?i=electronics&bbn=21832880031&rh=n%3A18018102031%2Cn%3A21832880031%2Cp_4%3AXO&dc&language=en_AE&ds=v1%3AkLVw3NbzC%2BaCZgcfoqLcbOPgEn7utZ7ifWlrQ8FztXg&pf_rd_i=18018102031&pf_rd_m=A1ZVRGNO5AYLOV&pf_rd_p=825c0142-9b0c-4a77-a6f2-b100f037e545&pf_rd_r=VF466KFA3FWQ7827B7MK&pf_rd_s=mobile-hybrid-12&pf_rd_t=30901&qid=1684156738&ref=sr_ex_n_1'

    # 取分類網址
    #url = 'https://www.amazon.eg/s?i=electronics&bbn=18018102031&rh=n%3A18018102031%2Cp_4%3AXO&dc&language=en_AE&ds=v1%3Aw8NdOFTPXuMQ0c%2F8YUAMuuNYUJ5DN%2FeWLDpLDLpTBWY&pf_rd_i=18018102031&pf_rd_m=A1ZVRGNO5AYLOV&pf_rd_p=825c0142-9b0c-4a77-a6f2-b100f037e545&pf_rd_r=VF466KFA3FWQ7827B7MK&pf_rd_s=mobile-hybrid-12&pf_rd_t=30901&qid=1684056263&ref=sr_ex_n_1'
    # 測試網址(短列表)
    #url='https://www.amazon.eg/s?i=electronics&bbn=21832968031&rh=n%3A18018102031%2Cn%3A21832880031%2Cn%3A21832968031%2Cn%3A21833106031%2Cp_4%3AXO&dc&language=en_AE&ds=v1%3AzaS0iYExgh7Qc%2BiAhvFEfP2OvROBLhGDqSIwGxcL2eE&pf_rd_i=18018102031&pf_rd_m=A1ZVRGNO5AYLOV&pf_rd_p=825c0142-9b0c-4a77-a6f2-b100f037e545&pf_rd_r=VF466KFA3FWQ7827B7MK&pf_rd_s=mobile-hybrid-12&pf_rd_t=30901&qid=1684157702&rnid=21832968031&ref=sr_nr_n_1'
    urls_list=[]
    ## 取商品資料




    #cat_id = 2
    urls = [
        'https://www.amazon.eg/s?i=electronics&bbn=18018103031&rh=n%3A18018102031%2Cn%3A21832871031%2Cp_4%3AXO&dc&language=en_AE&ds=v1%3ALqFkO4vJ9G9izb9yqVdx7g1JPAsO7%2FF3a2ZlWVgxpHI&pf_rd_i=18018102031&pf_rd_m=A1ZVRGNO5AYLOV&pf_rd_p=825c0142-9b0c-4a77-a6f2-b100f037e545&pf_rd_r=VF466KFA3FWQ7827B7MK&pf_rd_s=mobile-hybrid-12&pf_rd_t=30901&qid=1684333054&rnid=18018103031&ref=sr_nr_n_1'
       ,'https://www.amazon.eg/-/en/s?i=electronics&bbn=18018103031&rh=n%3A18018102031%2Cn%3A21832871031%2Cp_4%3AXO&dc&page=2&language=en_AE&pf_rd_i=18018102031&pf_rd_m=A1ZVRGNO5AYLOV&pf_rd_p=825c0142-9b0c-4a77-a6f2-b100f037e545&pf_rd_r=VF466KFA3FWQ7827B7MK&pf_rd_s=mobile-hybrid-12&pf_rd_t=30901&qid=1684333066&rnid=18018103031&ref=sr_pg_2'
    ]
    urls_list.append(urls)
    # cat_id = 3
    urls = [
            'https://www.amazon.eg/s?i=electronics&bbn=18018103031&rh=n%3A18018102031%2Cn%3A21832872031%2Cp_4%3AXO&dc&language=en_AE&ds=v1%3AlF%2FtzS9nEEYoNTM5EOG9T8YXJyTMGLpMhO6gFp3IXes&pf_rd_i=18018102031&pf_rd_m=A1ZVRGNO5AYLOV&pf_rd_p=825c0142-9b0c-4a77-a6f2-b100f037e545&pf_rd_r=VF466KFA3FWQ7827B7MK&pf_rd_s=mobile-hybrid-12&pf_rd_t=30901&qid=1684333086&rnid=18018103031&ref=sr_nr_n_2'
         , 'https://www.amazon.eg/-/en/s?i=electronics&bbn=18018103031&rh=n%3A18018102031%2Cn%3A21832872031%2Cp_4%3AXO&dc&page=2&language=en_AE&pf_rd_i=18018102031&pf_rd_m=A1ZVRGNO5AYLOV&pf_rd_p=825c0142-9b0c-4a77-a6f2-b100f037e545&pf_rd_r=VF466KFA3FWQ7827B7MK&pf_rd_s=mobile-hybrid-12&pf_rd_t=30901&qid=1684333088&rnid=18018103031&ref=sr_pg_2'
         , 'https://www.amazon.eg/-/en/s?i=electronics&bbn=18018103031&rh=n%3A18018102031%2Cn%3A21832872031%2Cp_4%3AXO&dc&page=3&language=en_AE&pf_rd_i=18018102031&pf_rd_m=A1ZVRGNO5AYLOV&pf_rd_p=825c0142-9b0c-4a77-a6f2-b100f037e545&pf_rd_r=VF466KFA3FWQ7827B7MK&pf_rd_s=mobile-hybrid-12&pf_rd_t=30901&qid=1684333127&rnid=18018103031&ref=sr_pg_3'
         , 'https://www.amazon.eg/-/en/s?i=electronics&bbn=18018103031&rh=n%3A18018102031%2Cn%3A21832872031%2Cp_4%3AXO&dc&page=4&language=en_AE&pf_rd_i=18018102031&pf_rd_m=A1ZVRGNO5AYLOV&pf_rd_p=825c0142-9b0c-4a77-a6f2-b100f037e545&pf_rd_r=VF466KFA3FWQ7827B7MK&pf_rd_s=mobile-hybrid-12&pf_rd_t=30901&qid=1684333132&rnid=18018103031&ref=sr_pg_4'
         , 'https://www.amazon.eg/-/en/s?i=electronics&bbn=18018103031&rh=n%3A18018102031%2Cn%3A21832872031%2Cp_4%3AXO&dc&page=5&language=en_AE&pf_rd_i=18018102031&pf_rd_m=A1ZVRGNO5AYLOV&pf_rd_p=825c0142-9b0c-4a77-a6f2-b100f037e545&pf_rd_r=VF466KFA3FWQ7827B7MK&pf_rd_s=mobile-hybrid-12&pf_rd_t=30901&qid=1684333143&rnid=18018103031&ref=sr_pg_5'
         , 'https://www.amazon.eg/-/en/s?i=electronics&bbn=18018103031&rh=n%3A18018102031%2Cn%3A21832872031%2Cp_4%3AXO&dc&page=6&language=en_AE&pf_rd_i=18018102031&pf_rd_m=A1ZVRGNO5AYLOV&pf_rd_p=825c0142-9b0c-4a77-a6f2-b100f037e545&pf_rd_r=VF466KFA3FWQ7827B7MK&pf_rd_s=mobile-hybrid-12&pf_rd_t=30901&qid=1684333153&rnid=18018103031&ref=sr_pg_6'
    ]
    urls_list.append(urls)

    # cat_id = 4
    urls = [
           'https://www.amazon.eg/s?i=electronics&bbn=18018103031&rh=n%3A18018102031%2Cn%3A21832869031%2Cp_4%3AXO&dc&language=en_AE&ds=v1%3A5rXzZsZEzbgqlGRbt7FdUaVEvS%2FsHEhQfzgMg%2B5zjJw&pf_rd_i=18018102031&pf_rd_m=A1ZVRGNO5AYLOV&pf_rd_p=825c0142-9b0c-4a77-a6f2-b100f037e545&pf_rd_r=VF466KFA3FWQ7827B7MK&pf_rd_s=mobile-hybrid-12&pf_rd_t=30901&qid=1684255290&rnid=18018103031&ref=sr_nr_n_3'
         , 'https://www.amazon.eg/-/en/s?i=electronics&bbn=18018103031&rh=n%3A18018102031%2Cn%3A21832869031%2Cp_4%3AXO&dc&page=2&language=en_AE&pf_rd_i=18018102031&pf_rd_m=A1ZVRGNO5AYLOV&pf_rd_p=825c0142-9b0c-4a77-a6f2-b100f037e545&pf_rd_r=VF466KFA3FWQ7827B7MK&pf_rd_s=mobile-hybrid-12&pf_rd_t=30901&qid=1684255296&rnid=18018103031&ref=sr_pg_2'
    ]
    urls_list.append(urls)

    # cat_id = 5
    urls = [
      'https://www.amazon.eg/s?i=electronics&bbn=18018103031&rh=n%3A18018102031%2Cn%3A21832880031%2Cp_4%3AXO&dc&language=en_AE&ds=v1%3AJ3RGruWA2Z62FSjTuuom071wLZbU5SiWFhkFhKEO28k&pf_rd_i=18018102031&pf_rd_m=A1ZVRGNO5AYLOV&pf_rd_p=825c0142-9b0c-4a77-a6f2-b100f037e545&pf_rd_r=VF466KFA3FWQ7827B7MK&pf_rd_s=mobile-hybrid-12&pf_rd_t=30901&qid=1684255290&rnid=18018103031&ref=sr_nr_n_4'
    ]
    urls_list.append(urls)

    # cat_id = 6
    urls = [
      'https://www.amazon.eg/s?i=electronics&bbn=18018103031&rh=n%3A18018102031%2Cn%3A21832881031%2Cp_4%3AXO&dc&language=en_AE&ds=v1%3ABTVdFdmSS1KTeqxw0BtZKm9%2BEto%2F4lQdjiyB2VZlC5U&pf_rd_i=18018102031&pf_rd_m=A1ZVRGNO5AYLOV&pf_rd_p=825c0142-9b0c-4a77-a6f2-b100f037e545&pf_rd_r=VF466KFA3FWQ7827B7MK&pf_rd_s=mobile-hybrid-12&pf_rd_t=30901&qid=1684255290&rnid=18018103031&ref=sr_nr_n_5'
     ,'https://www.amazon.eg/-/en/s?i=electronics&bbn=18018103031&rh=n%3A18018102031%2Cn%3A21832881031%2Cp_4%3AXO&dc&page=2&language=en_AE&pf_rd_i=18018102031&pf_rd_m=A1ZVRGNO5AYLOV&pf_rd_p=825c0142-9b0c-4a77-a6f2-b100f037e545&pf_rd_r=VF466KFA3FWQ7827B7MK&pf_rd_s=mobile-hybrid-12&pf_rd_t=30901&qid=1684255471&rnid=18018103031&ref=sr_pg_2'
     ,'https://www.amazon.eg/-/en/s?i=electronics&bbn=18018103031&rh=n%3A18018102031%2Cn%3A21832881031%2Cp_4%3AXO&dc&page=3&language=en_AE&pf_rd_i=18018102031&pf_rd_m=A1ZVRGNO5AYLOV&pf_rd_p=825c0142-9b0c-4a77-a6f2-b100f037e545&pf_rd_r=VF466KFA3FWQ7827B7MK&pf_rd_s=mobile-hybrid-12&pf_rd_t=30901&qid=1684255473&rnid=18018103031&ref=sr_pg_3'
     ,'https://www.amazon.eg/-/en/s?i=electronics&bbn=18018103031&rh=n%3A18018102031%2Cn%3A21832881031%2Cp_4%3AXO&dc&page=4&language=en_AE&pf_rd_i=18018102031&pf_rd_m=A1ZVRGNO5AYLOV&pf_rd_p=825c0142-9b0c-4a77-a6f2-b100f037e545&pf_rd_r=VF466KFA3FWQ7827B7MK&pf_rd_s=mobile-hybrid-12&pf_rd_t=30901&qid=1684255555&rnid=18018103031&ref=sr_pg_4'
    ]
    urls_list.append(urls)

    # cat_id =7
    urls = [
       'https://www.amazon.eg/s?i=electronics&bbn=18018103031&rh=n%3A18018102031%2Cn%3A21832868031%2Cp_4%3AXO&dc&language=en_AE&ds=v1%3As2iA75R1Nb3D6dx3scOM4qFImcFV8gG7Xpcoym1p71k&pf_rd_i=18018102031&pf_rd_m=A1ZVRGNO5AYLOV&pf_rd_p=825c0142-9b0c-4a77-a6f2-b100f037e545&pf_rd_r=VF466KFA3FWQ7827B7MK&pf_rd_s=mobile-hybrid-12&pf_rd_t=30901&qid=1684256007&rnid=18018103031&ref=sr_nr_n_6'
     , 'https://www.amazon.eg/-/en/s?i=electronics&bbn=18018103031&rh=n%3A18018102031%2Cn%3A21832868031%2Cp_4%3AXO&dc&page=2&language=en_AE&pf_rd_i=18018102031&pf_rd_m=A1ZVRGNO5AYLOV&pf_rd_p=825c0142-9b0c-4a77-a6f2-b100f037e545&pf_rd_r=VF466KFA3FWQ7827B7MK&pf_rd_s=mobile-hybrid-12&pf_rd_t=30901&qid=1684256009&rnid=18018103031&ref=sr_pg_2'
     , 'https://www.amazon.eg/-/en/s?i=electronics&bbn=18018103031&rh=n%3A18018102031%2Cn%3A21832868031%2Cp_4%3AXO&dc&page=3&language=en_AE&pf_rd_i=18018102031&pf_rd_m=A1ZVRGNO5AYLOV&pf_rd_p=825c0142-9b0c-4a77-a6f2-b100f037e545&pf_rd_r=VF466KFA3FWQ7827B7MK&pf_rd_s=mobile-hybrid-12&pf_rd_t=30901&qid=1684256012&rnid=18018103031&ref=sr_pg_3'
     , 'https://www.amazon.eg/-/en/s?i=electronics&bbn=18018103031&rh=n%3A18018102031%2Cn%3A21832868031%2Cp_4%3AXO&dc&page=4&language=en_AE&pf_rd_i=18018102031&pf_rd_m=A1ZVRGNO5AYLOV&pf_rd_p=825c0142-9b0c-4a77-a6f2-b100f037e545&pf_rd_r=VF466KFA3FWQ7827B7MK&pf_rd_s=mobile-hybrid-12&pf_rd_t=30901&qid=1684256069&rnid=18018103031&ref=sr_pg_4'
     , 'https://www.amazon.eg/-/en/s?i=electronics&bbn=18018103031&rh=n%3A18018102031%2Cn%3A21832868031%2Cp_4%3AXO&dc&page=5&language=en_AE&pf_rd_i=18018102031&pf_rd_m=A1ZVRGNO5AYLOV&pf_rd_p=825c0142-9b0c-4a77-a6f2-b100f037e545&pf_rd_r=VF466KFA3FWQ7827B7MK&pf_rd_s=mobile-hybrid-12&pf_rd_t=30901&qid=1684256104&rnid=18018103031&ref=sr_pg_5'
     , 'https://www.amazon.eg/-/en/s?i=electronics&bbn=18018103031&rh=n%3A18018102031%2Cn%3A21832868031%2Cp_4%3AXO&dc&page=6&language=en_AE&pf_rd_i=18018102031&pf_rd_m=A1ZVRGNO5AYLOV&pf_rd_p=825c0142-9b0c-4a77-a6f2-b100f037e545&pf_rd_r=VF466KFA3FWQ7827B7MK&pf_rd_s=mobile-hybrid-12&pf_rd_t=30901&qid=1684256135&rnid=18018103031&ref=sr_pg_6'
     , 'https://www.amazon.eg/-/en/s?i=electronics&bbn=18018103031&rh=n%3A18018102031%2Cn%3A21832868031%2Cp_4%3AXO&dc&page=7&language=en_AE&pf_rd_i=18018102031&pf_rd_m=A1ZVRGNO5AYLOV&pf_rd_p=825c0142-9b0c-4a77-a6f2-b100f037e545&pf_rd_r=VF466KFA3FWQ7827B7MK&pf_rd_s=mobile-hybrid-12&pf_rd_t=30901&qid=1684256222&rnid=18018103031&ref=sr_pg_7'
     , 'https://www.amazon.eg/-/en/s?i=electronics&bbn=18018103031&rh=n%3A18018102031%2Cn%3A21832868031%2Cp_4%3AXO&dc&page=8&language=en_AE&pf_rd_i=18018102031&pf_rd_m=A1ZVRGNO5AYLOV&pf_rd_p=825c0142-9b0c-4a77-a6f2-b100f037e545&pf_rd_r=VF466KFA3FWQ7827B7MK&pf_rd_s=mobile-hybrid-12&pf_rd_t=30901&qid=1684256225&rnid=18018103031&ref=sr_pg_8'
     , 'https://www.amazon.eg/-/en/s?i=electronics&bbn=18018103031&rh=n%3A18018102031%2Cn%3A21832868031%2Cp_4%3AXO&dc&page=9&language=en_AE&pf_rd_i=18018102031&pf_rd_m=A1ZVRGNO5AYLOV&pf_rd_p=825c0142-9b0c-4a77-a6f2-b100f037e545&pf_rd_r=VF466KFA3FWQ7827B7MK&pf_rd_s=mobile-hybrid-12&pf_rd_t=30901&qid=1684256256&rnid=18018103031&ref=sr_pg_9'
    ]
    urls_list.append(urls)

    ##Portable Sound & Vision
    # cat_id = 8
    urls = [
      'https://www.amazon.eg/s?i=electronics&bbn=18018103031&rh=n%3A18018102031%2Cn%3A21832877031%2Cp_4%3AXO&dc&language=en_AE&ds=v1%3AoAZWWIp3rZli2IJ3clj4I3SsjBu7kYVZTE%2B1KEBdTRw&pf_rd_i=18018102031&pf_rd_m=A1ZVRGNO5AYLOV&pf_rd_p=825c0142-9b0c-4a77-a6f2-b100f037e545&pf_rd_r=VF466KFA3FWQ7827B7MK&pf_rd_s=mobile-hybrid-12&pf_rd_t=30901&qid=1684256333&rnid=18018103031&ref=sr_nr_n_7'
     ,'https://www.amazon.eg/-/en/s?i=electronics&bbn=18018103031&rh=n%3A18018102031%2Cn%3A21832877031%2Cp_4%3AXO&dc&page=2&language=en_AE&pf_rd_i=18018102031&pf_rd_m=A1ZVRGNO5AYLOV&pf_rd_p=825c0142-9b0c-4a77-a6f2-b100f037e545&pf_rd_r=VF466KFA3FWQ7827B7MK&pf_rd_s=mobile-hybrid-12&pf_rd_t=30901&qid=1684256336&rnid=18018103031&ref=sr_pg_2'
     ,'https://www.amazon.eg/-/en/s?i=electronics&bbn=18018103031&rh=n%3A18018102031%2Cn%3A21832877031%2Cp_4%3AXO&dc&page=3&language=en_AE&pf_rd_i=18018102031&pf_rd_m=A1ZVRGNO5AYLOV&pf_rd_p=825c0142-9b0c-4a77-a6f2-b100f037e545&pf_rd_r=VF466KFA3FWQ7827B7MK&pf_rd_s=mobile-hybrid-12&pf_rd_t=30901&qid=1684256339&rnid=18018103031&ref=sr_pg_3'
     ,'https://www.amazon.eg/-/en/s?i=electronics&bbn=18018103031&rh=n%3A18018102031%2Cn%3A21832877031%2Cp_4%3AXO&dc&page=4&language=en_AE&pf_rd_i=18018102031&pf_rd_m=A1ZVRGNO5AYLOV&pf_rd_p=825c0142-9b0c-4a77-a6f2-b100f037e545&pf_rd_r=VF466KFA3FWQ7827B7MK&pf_rd_s=mobile-hybrid-12&pf_rd_t=30901&qid=1684256388&rnid=18018103031&ref=sr_pg_4'
    ]
    urls_list.append(urls)

    # cat_id = 9
    urls = [
       'https://www.amazon.eg/s?i=electronics&bbn=18018103031&rh=n%3A18018102031%2Cn%3A21832874031%2Cp_4%3AXO&dc&language=en_AE&ds=v1%3AlQJfii5eR7zHgaF1zQ3Uihg8gRpZYl2e9ZetEUG2zqc&pf_rd_i=18018102031&pf_rd_m=A1ZVRGNO5AYLOV&pf_rd_p=825c0142-9b0c-4a77-a6f2-b100f037e545&pf_rd_r=VF466KFA3FWQ7827B7MK&pf_rd_s=mobile-hybrid-12&pf_rd_t=30901&qid=1684256416&rnid=18018103031&ref=sr_nr_n_8'
    ]
    urls_list.append(urls)

    # cat_id =10
    urls = [
      'https://www.amazon.eg/s?i=electronics&bbn=18018103031&rh=n%3A18018102031%2Cn%3A21832882031%2Cp_4%3AXO&dc&language=en_AE&ds=v1%3AZQEEvYHSUVA4mJ0eh6LuJ5bEA6EA544D2Dp%2FFMqubTw&pf_rd_i=18018102031&pf_rd_m=A1ZVRGNO5AYLOV&pf_rd_p=825c0142-9b0c-4a77-a6f2-b100f037e545&pf_rd_r=VF466KFA3FWQ7827B7MK&pf_rd_s=mobile-hybrid-12&pf_rd_t=30901&qid=1684256459&rnid=18018103031&ref=sr_nr_n_9'
      ,'https://www.amazon.eg/-/en/s?i=electronics&bbn=18018103031&rh=n%3A18018102031%2Cn%3A21832882031%2Cp_4%3AXO&dc&page=2&language=en_AE&pf_rd_i=18018102031&pf_rd_m=A1ZVRGNO5AYLOV&pf_rd_p=825c0142-9b0c-4a77-a6f2-b100f037e545&pf_rd_r=VF466KFA3FWQ7827B7MK&pf_rd_s=mobile-hybrid-12&pf_rd_t=30901&qid=1684256463&rnid=18018103031&ref=sr_pg_2'
      ,'https://www.amazon.eg/-/en/s?i=electronics&bbn=18018103031&rh=n%3A18018102031%2Cn%3A21832882031%2Cp_4%3AXO&dc&page=3&language=en_AE&pf_rd_i=18018102031&pf_rd_m=A1ZVRGNO5AYLOV&pf_rd_p=825c0142-9b0c-4a77-a6f2-b100f037e545&pf_rd_r=VF466KFA3FWQ7827B7MK&pf_rd_s=mobile-hybrid-12&pf_rd_t=30901&qid=1684256465&rnid=18018103031&ref=sr_pg_3'
    ]
    urls_list.append(urls)

    # cat_id = 11
    urls = [
    'https://www.amazon.eg/s?i=electronics&bbn=18018103031&rh=n%3A18018102031%2Cn%3A21832878031%2Cp_4%3AXO&dc&language=en_AE&ds=v1%3ASaIqHNaWFM%2FVFkP0%2Fwzf40zLDV79OaVHc6%2BBl4VtMho&pf_rd_i=18018102031&pf_rd_m=A1ZVRGNO5AYLOV&pf_rd_p=825c0142-9b0c-4a77-a6f2-b100f037e545&pf_rd_r=VF466KFA3FWQ7827B7MK&pf_rd_s=mobile-hybrid-12&pf_rd_t=30901&qid=1684256459&rnid=18018103031&ref=sr_nr_n_10'
    ]
    urls_list.append(urls)

    cat_id = 2
    start_id = 1
    for urls_list_index in range(0, len(urls_list)):
        for url_num_Index in range(0, len(urls_list[urls_list_index])):
            print(str(cat_id) + '類 開始' + str(url_num_Index) + '頁-------------------------')
            print(str(cat_id) + '類 開始' + str(url_num_Index) + '頁-------------------------')
            print(str(cat_id) + '類 開始' + str(url_num_Index) + '頁-------------------------')
            start_id = await product_list_web_crawler(urls_list[urls_list_index][url_num_Index], start_id, cat_id)
            print('目前打印完' + str(url_num_Index) + '頁，共', start_id, '筆')
            print('目前打印完' + str(url_num_Index) + '頁，共', start_id, '筆')
            print('目前打印完' + str(url_num_Index) + '頁，共', start_id, '筆')
            time.sleep(0.5)
        cat_id += 1
    print('完成')

    ## 取分類表
    #await get_categories(url)





asyncio.run(main())
