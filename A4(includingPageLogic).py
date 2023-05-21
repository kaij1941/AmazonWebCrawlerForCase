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
from selenium.webdriver.common.action_chains import ActionChains
import concurrent.futures

# For A4-----------------------------------------------
# For A4-----------------------------------------------
# For A4-----------------------------------------------
# For A4-----------------------------------------------

db_Doing = False
db_True = True #是否為正式DB

headers = httpx.Headers({
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
    'cookie': 'session-id=257-2028996-0896043; i18n-prefs=EGP; lc-acbeg=en_AE; ubid-acbeg=261-1798037-1499267; session-id-time=2082787201l; session-token=lTKhbG4Udz66QrWRIjnEK1rIGOjJh7oHQ7qE3DU++H+8t6b7fxWe7YXQDdfytAXhKxVYVbpH4W/vYUzyCFw/e1/pQAUxgBjoHHrhcgxGm4Nn4rPOOw+IlnX4THjoXO7vaIR21GNvriFz6J3iovRnI6ie9jyHr/q0ZgnUoVF01ymSiKG98Rs9hSNn830FeGM3yGtxBQ0YMJEmWYuT6waUwIhl+GzhqyXEK9/DGQDGokQ=; csm-hit=tb:s-N7M0X2V9YV3G1AWZ7ZX4|1684168857815&t:1684168858301&adb:adblk_yes',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
    'Origin': 'https://www.amazon.eg'
})

async def fetch_url(url):
    """
    非同步獲取網址的函數。

    參數：
    url -- 要獲取的網址

    返回值：
    獲取的網頁內容

    使用非同步方式向指定的網址發送請求，獲取網頁的內容並返回。

    """
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

async def web_crawler_with_selenium(url):
    # 非必要不使用 selenium,效能問題
    webdriver_path = '/path/to/chromedriver'

    # 设置 Chrome 选项
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # 无界面模式

    # 创建 Chrome WebDriver
    driver = webdriver.Chrome(service=Service(webdriver_path), options=chrome_options)
    # 打开目标网页
    driver.get(url)
    # 等待页面加载
    driver.implicitly_wait(0.1)
    # 设置请求头
    for key, value in headers.items():
        driver.execute_cdp_cmd("Network.setExtraHTTPHeaders", {"headers": {key: value}})

    # 定位父元素
    parent_element = driver.find_element(By.ID, 'altImages')

    # 定位所有的imageThumbnail元素
    thumbnail_elements = driver.find_elements(By.CSS_SELECTOR, '.imageThumbnail')

    # 创建ActionChains对象
    actions = ActionChains(driver)

    def slide_thumbnail(thumbnail_element):
        # 找到img元素
        img_element = thumbnail_element.find_element('tag name', 'img')

        # 模拟将鼠标移动到img元素上
        actions.move_to_element(img_element).perform()

    # 并行处理元素滑动
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # 提交任务并返回Future对象
        futures = [executor.submit(slide_thumbnail, thumbnail_element) for thumbnail_element in thumbnail_elements]

        # 等待所有任务完成
        concurrent.futures.wait(futures)


    # 获取网页的HTML源代码
    html = driver.page_source
    driver.quit()
    return html




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
    if db_True :
        conn = await aiomysql.connect(
            host="8.218.38.94",
            user="woshop",
            password="DLpPbHtiMKw28sfE",
            db="woshop_db"
        )
    else:
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
    if db_True :
        conn = await aiomysql.connect(
            host="8.218.38.94",
            user="woshop",
            password="DLpPbHtiMKw28sfE",
            db="woshop_db"
        )
    else:
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
                    marketprice = [float(element) * 1.2 for element in price_array[price_index]]
                else:
                    marketprice = float(price_array[price_index]) * 1.2
            price_index += 1
        marketprice_array.append(marketprice)

    # thumb_img
    thumbnail_elements = soup.select('.s-image')
    for thumbnail_element in thumbnail_elements:
        thumbnail_url = thumbnail_element['src']
        thumb_img_array.append(remove_number_from_url(thumbnail_url))

    # 開始處理個別商品頁的資訊
    print("開始", len(productnames_array), '筆品項')

    # 搜尋個別商品頁面，獲取更多商品圖片和描述
    image_urls = []

    # 取得個別商品頁連結(因為有一個商品在列表中有多個連結所以 會有多個資訊)
    item_links = soup.select('.s-product-image-container .a-link-normal ')
    # print("item_links:", len(item_links))
    numitem_link = 0
    print('開始抓圖片起始點', "=>item_links:", len(item_links))
    for item_link in item_links:
        numitem_link += 1
        time.sleep(0.1)
        print("開始抓圖片:", numitem_link)
        pic_count = 0
        if item_link:
            item_url = item_link['href']
            item_url = 'https://www.amazon.eg' + item_url
            item_html = await web_crawler_with_selenium(item_url)
            item_soup = BeautifulSoup(item_html, 'html.parser')
            # print("開始抓圖片:", numitem_link)
            # 獲取商品描述
            # print("開始抓圖片:", numitem_link, '=>商品描述')
            description_element = item_soup.select_one('#productDescription .a-unordered-list')
            description = description_element.text.strip() if description_element else '無商品描述'
            product_desc.append(description)

            # 尋找所有商品圖片的URL
            # print("開始抓圖片:", numitem_link, '=>Url')
            img_elements = item_soup.select('.a-list-item .imgTagWrapper img')
            for img_element in img_elements:
                image_url = img_element.get('data-old-hires')
                if image_url is None or len(image_url.strip()) == 0:
                    image_url = img_element.get('src')
                image_url = remove_number_from_url(image_url)
                image_urls.append(image_url)
                # print(image_url)
                pic_count += 1
            product_piccount.append(pic_count)
            product_pics.append(image_urls)
    # 印出商品流水號（Id）、商品名稱和價格
    skip = 0
    product_pic_index = 0
    # 因為會有沒價格跳過的調整項
    id_minus = 0
    for num in range(0, len(productnames_array)):
        if num in skipItem:
            id_minus += 1
            continue
        print('開始寫入DB =>', "Id:", id_array[num]-id_minus, '------------------------------------------------')
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
            product_pic_index += product_piccount[picnum]
            continue
        product_pic_self_index = 0
        for product_pic_count in range(0, product_piccount[picnum]):
            if product_pic_index < len(product_pics[0]):
                print(product_pic_index, '.:', product_pics[0][product_pic_index])
                # DB填寫
                # add_newdata_to_sp_goods_pic_ 填寫
                await add_newdata_to_sp_goods_pic_(id_array[picnum]-id_minus, product_pics[0][product_pic_index], product_pic_self_index)
                product_pic_index += 1
                product_pic_self_index += 1
    return int(id_array[-1]+1-id_minus)

def remove_number_from_url(url):
    """
    從URL中移除數字的函數

    參數：
    url (str)：要處理的URL

    返回值：
    str：移除數字後的新URL
    """
    pattern = r"(_AC_[A-Z]+)\d+"  # 正則表達式模式，匹配含有數字的部分
    new_url = re.sub(pattern, r"\1", url)  # 使用匹配的子串替換數字部分
    return new_url

async def get_categories(url,cat_id,parent_id,sort):
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
        category_item = category.text.strip()
        if len(category_item) > 0:
            category_list.append(category.text.strip())

    # 关闭 WebDriver
    driver.quit()
    if len(category_list) > 1:
        parent_index = 1
        print('父類別' + str(cat_id) + ':' + category_list[parent_index])
        await add_newdata_to_sp_category_(cat_id, category_list[parent_index], 0, sort)
        # 打印类别列表
        for category_index in range(2, len(category_list)):
            cat_id += 1
            sort += 1
            await add_newdata_to_sp_category_(cat_id, category_list[category_index], parent_id, sort)
            print('子類(延續父類'+category_list[parent_index]+')', category_list[category_index])
    return categories

async def main():
    """
    主函數的非同步實現。

    該函數是整個程序的入口，用於協調和調用其他非同步函數。
    在主函數內，可以根據具體需求執行一系列的非同步任務，例如發送請求、解析數據等。
    通常，主函數會使用 `await` 關鍵字來等待非同步操作的完成，以確保程序的順序執行。

    """
    # 測試網址(短列表)
    # url='https://www.amazon.eg/s?i=electronics&bbn=21832968031&rh=n%3A18018102031%2Cn%3A21832880031%2Cn%3A21832968031%2Cn%3A21833106031%2Cp_4%3AXO&dc&language=en_AE&ds=v1%3AzaS0iYExgh7Qc%2BiAhvFEfP2OvROBLhGDqSIwGxcL2eE&pf_rd_i=18018102031&pf_rd_m=A1ZVRGNO5AYLOV&pf_rd_p=825c0142-9b0c-4a77-a6f2-b100f037e545&pf_rd_r=VF466KFA3FWQ7827B7MK&pf_rd_s=mobile-hybrid-12&pf_rd_t=30901&qid=1684157702&rnid=21832968031&ref=sr_nr_n_1'

    # 取商品資料
    # 取列表網址
    urls_list = []
    urls = [
    # 1
    #     'https://www.amazon.eg/-/en/s?i=electronics&rh=n%3A21832883031&fs=true&language=en&qid=1684566298&ref=sr_pg_1'
    #     ,'https://www.amazon.eg/-/en/s?i=electronics&rh=n%3A21832883031&fs=true&page=2&language=en&qid=1684566670&ref=sr_pg_2'
    #     ,'https://www.amazon.eg/-/en/s?i=electronics&rh=n%3A21832883031&fs=true&page=3&language=en&qid=1684566775&ref=sr_pg_3'
    #     ,'https://www.amazon.eg/s?i=electronics&rh=n%3A21832883031&fs=true&page=4&language=en&qid=1684566783&ref=sr_pg_4'
    #     ,'https://www.amazon.eg/s?i=electronics&rh=n%3A21832883031&fs=true&page=5&language=en&qid=1684566774&ref=sr_pg_5'
    # # 6
    #     ,'https://www.amazon.eg/-/en/s?i=electronics&rh=n%3A21832883031&fs=true&page=6&language=en&qid=1684566832&ref=sr_pg_6'
    #     ,'https://www.amazon.eg/-/en/s?i=electronics&rh=n%3A21832883031&fs=true&page=7&language=en&qid=1684566834&ref=sr_pg_7'
    #      'https://www.amazon.eg/-/en/s?i=electronics&rh=n%3A21832883031&fs=true&page=8&language=en&qid=1684566845&ref=sr_pg_8'
        #,
        'https://www.amazon.eg/-/en/s?i=electronics&rh=n%3A21832883031&fs=true&page=9&language=en&qid=1684566856&ref=sr_pg_9'
    ]

    urls_list.append(urls)

    cat_id = 12
    start_id =821
    end_id = 616 + 200
    for urls_list_index in range(0, len(urls_list)):
        if start_id > end_id:
            print('已打印完', str(start_id), '提早結束(' + str(end_id) + ')')
            print('完成')
            return
        for url_num_Index in range(0, len(urls_list[urls_list_index])):
            print(str(cat_id) + '類 開始' + str(url_num_Index+1) + '頁--------------------------------------------------')
            print(str(cat_id) + '類 開始' + str(url_num_Index+1) + '頁--------------------------------------------------')
            print(str(cat_id) + '類 開始' + str(url_num_Index+1) + '頁--------------------------------------------------')
            print(str(cat_id) + '類 開始' + str(url_num_Index+1) + '頁--------------------------------------------------')
            start_id = await product_list_web_crawler(urls_list[urls_list_index][url_num_Index], start_id, cat_id)
            print('目前打印完' + str(cat_id) + '類' + str(url_num_Index+1) + '頁，共', start_id, '筆')
            print('目前打印完' + str(cat_id) + '類' + str(url_num_Index+1) + '頁，共', start_id, '筆')
            print('目前打印完' + str(cat_id) + '類' + str(url_num_Index+1) + '頁，共', start_id, '筆')
            print('目前打印完' + str(cat_id) + '類' + str(url_num_Index+1) + '頁，共', start_id, '筆')

            if start_id > end_id:
                print('已打印完', str(start_id), '提早結束('+str(end_id)+')')
                continue
            time.sleep(0.3)
        cat_id += 1



    ## 取分類表
    # 取分類網址
    # url = 'https://www.amazon.eg/-/en/s?i=electronics&rh=n%3A21832883031&fs=true&language=en&qid=1684563659&ref=sr_pg_1'
    # cat_id = 12
    # parent_id = 12
    # sort = 12
    # await get_categories(url, cat_id, parent_id, sort)

    print('完成')



asyncio.run(main())
