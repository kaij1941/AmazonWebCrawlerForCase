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

db_Doing = True
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


async def web_crawler_with_selenium(url, isProductDetail = True):
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

    waitTime = 0.1 if isProductDetail else 1
    driver.implicitly_wait(waitTime)
    # 设置请求头
    for key, value in headers.items():
        driver.execute_cdp_cmd("Network.setExtraHTTPHeaders", {"headers": {key: value}})
    if isProductDetail:
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
            db="woshop_db",
            charset='utf8mb4'
        )
    else:
        conn = await aiomysql.connect(
            host="localhost",
            port=3306,
            user="root",
            password="J2294140319",
            db="woshop_db",
            charset='utf8mb4'
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
    if db_True:
        conn = await aiomysql.connect(
            host="8.218.38.94",
            user="woshop",
            password="DLpPbHtiMKw28sfE",
            db="woshop_db",
            charset='utf8mb4'
        )
    else:
        conn = await aiomysql.connect(
            host="localhost",
            port=3306,
            user="root",
            password="J2294140319",
            db="woshop_db",
            charset='utf8mb4'
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
    sql = "select count(1) from sp_goods where id=%s and goods_name=%s COLLATE utf8mb4_general_ci  LIMIT 1"
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
    product_names = soup.select('.s-card-container .a-size-medium')
    name_index = 0
    for product_name in product_names:
        productnames_array.append(product_name.text.strip())
        print(product_name.text.strip())
        id_array.append(start_id)
        if '🇺🇸' in product_name.text.strip():
            skipItem.append(name_index)
        start_id += 1
        name_index += 1

    # === 銷售價格 === price_element
    # === 市場價格 === marketprice_elements
    items = soup.select('.s-card-container')
    for index, item in enumerate(items, 1):
        price_element = item.select_one('.a-offscreen')
        if price_element is not None and price_element:
            price = re.sub(r'[^\d.]', '', price_element.text.strip())
            marketprice_element = item.select_one('.a-text-price .a-offscreen')
            if marketprice_element:
                marketprice = re.sub(r'[^\d.]', '', marketprice_element.text.strip())
            else:
                marketprice = float(price) * 1.2
        else:
            price = '無價格資訊'
            marketprice = 0.0
            skipItem.append(index-1)
        marketprice_array.append(marketprice)
        price_array.append(price)

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
        parent_index = 0
        print('父類別' + str(cat_id) + ':' + category_list[parent_index])
        await add_newdata_to_sp_category_(cat_id, category_list[parent_index], 0, sort)
        # 打印类别列表
        for category_index in range(parent_index+1, len(category_list)):
            cat_id += 1
            sort += 1
            await add_newdata_to_sp_category_(cat_id, category_list[category_index], parent_id, sort)
            print('子類(延續父類'+category_list[parent_index]+')', str(cat_id), category_list[category_index])
    return categories

async def get_pagesUrl(url,pages):
    if url == '':
        print('網址異常')
    # 1
    print('# 1')
    print("'" + url + "'")

    html = await fetch_url(url)
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.select('.s-pagination-container a')
    url = 'https://www.amazon.eg' + items[0]['href']
    # 2
    print(",'" + url + "'")
    url = 'https://www.amazon.eg' + items[1]['href']
    # 3
    print(",'" + url + "'")
    url_list = []
    for pageCount in range(4, pages+1):
        html = await fetch_url(url)
        soup = BeautifulSoup(html, 'html.parser')
        items = soup.select('.s-pagination-container a')
        if pageCount % 5 == 1:
           print('#', str(pageCount))
        if pageCount < 6:
            url = 'https://www.amazon.eg' + items[pageCount-1]['href']
        else:
            url = 'https://www.amazon.eg' + items[4]['href']
        if url not in url_list:
            url_list.append(url)
            print(",'" + url + "'")


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
    # 測試五筆狀況用
    # 'https://www.amazon.eg/-/en/s?i=videogames&bbn=21868821031&rh=n%3A18022560031%2Cn%3A21868821031%2Cp_36%3A73500-74000%2Cp_72%3A21909186031&dc&fs=true&language=en&qid=1684593825&rnid=21909183031&ref=sr_nr_p_72_2&ds=v1%3A8q5d2GXiGN7T1zXRKBW6yyJT8OXti82kZFRUXNw1dsI'
    # 15 Legacy Systems
    # urls = [
    #     # 1
    #     'https://www.amazon.eg/s?i=videogames&bbn=18022561031&rh=n%3A18022560031%2Cn%3A21868827031&dc&fs=true&language=en&ds=v1%3A54MjgwfY2OC9ckFFHLAG7ajsMm5WoVkXEsSTqGe9Nhg&qid=1684593140&rnid=18022561031&ref=sr_nr_n_1'
    #     ,'https://www.amazon.eg/-/en/s?i=videogames&bbn=18022561031&rh=n%3A18022560031%2Cn%3A21868827031&dc&fs=true&page=2&language=en&qid=1684595404&rnid=18022561031&ref=sr_pg_2'
    #     ,'https://www.amazon.eg/-/en/s?i=videogames&bbn=18022561031&rh=n%3A18022560031%2Cn%3A21868827031&dc&fs=true&page=3&language=en&qid=1684595429&rnid=18022561031&ref=sr_pg_3'
    #     ,'https://www.amazon.eg/-/en/s?i=videogames&bbn=18022561031&rh=n%3A18022560031%2Cn%3A21868827031&dc&fs=true&page=4&language=en&qid=1684595442&rnid=18022561031&ref=sr_pg_4'
    #     ,'https://www.amazon.eg/-/en/s?i=videogames&bbn=18022561031&rh=n%3A18022560031%2Cn%3A21868827031&dc&fs=true&page=5&language=en&qid=1684595458&rnid=18022561031&ref=sr_pg_5'
    #     # 6
    #     ,'https://www.amazon.eg/-/en/s?i=videogames&bbn=18022561031&rh=n%3A18022560031%2Cn%3A21868827031&dc&fs=true&page=6&language=en&qid=1684595466&rnid=18022561031&ref=sr_pg_6'
    #     ,'https://www.amazon.eg/-/en/s?i=videogames&bbn=18022561031&rh=n%3A18022560031%2Cn%3A21868827031&dc&fs=true&page=7&language=en&qid=1684595473&rnid=18022561031&ref=sr_pg_7'
    #     ,'https://www.amazon.eg/-/en/s?i=videogames&bbn=18022561031&rh=n%3A18022560031%2Cn%3A21868827031&dc&fs=true&page=8&language=en&qid=1684595481&rnid=18022561031&ref=sr_pg_8'
    #     ,'https://www.amazon.eg/-/en/s?i=videogames&bbn=18022561031&rh=n%3A18022560031%2Cn%3A21868827031&dc&fs=true&page=9&language=en&qid=1684595490&rnid=18022561031&ref=sr_pg_9'
    #     ,'https://www.amazon.eg/-/en/s?i=videogames&bbn=18022561031&rh=n%3A18022560031%2Cn%3A21868827031&dc&fs=true&page=10&language=en&qid=1684595498&rnid=18022561031&ref=sr_pg_10'
    #     # 11
    #      ,'https://www.amazon.eg/-/en/s?i=videogames&bbn=18022561031&rh=n%3A18022560031%2Cn%3A21868827031&dc&fs=true&page=11&language=en&qid=1684595513&rnid=18022561031&ref=sr_pg_11'
    #      ,'https://www.amazon.eg/-/en/s?i=videogames&bbn=18022561031&rh=n%3A18022560031%2Cn%3A21868827031&dc&fs=true&page=12&language=en&qid=1684595550&rnid=18022561031&ref=sr_pg_12'
    #      ,'https://www.amazon.eg/-/en/s?i=videogames&bbn=18022561031&rh=n%3A18022560031%2Cn%3A21868827031&dc&fs=true&page=13&language=en&qid=1684595571&rnid=18022561031&ref=sr_pg_13'
    #      ,'https://www.amazon.eg/-/en/s?i=videogames&bbn=18022561031&rh=n%3A18022560031%2Cn%3A21868827031&dc&fs=true&page=14&language=en&qid=1684595580&rnid=18022561031&ref=sr_pg_14'
    #      ,'https://www.amazon.eg/-/en/s?i=videogames&bbn=18022561031&rh=n%3A18022560031%2Cn%3A21868827031&dc&fs=true&page=15&language=en&qid=1684595589&rnid=18022561031&ref=sr_pg_15'
    # ]
    # urls_list.append(urls)
    #
    # # 16 Linux Games
    # urls = [
    #     # 1
    #     'https://www.amazon.eg/s?i=videogames&bbn=18022561031&rh=n%3A18022560031%2Cn%3A21868825031&dc&fs=true&language=en&ds=v1%3AaH1cvk6EhcNVZa4Pb2DpZ%2BDogHrb9TH%2F4AaH4AQY1PM&qid=1684595868&rnid=18022561031&ref=sr_nr_n_2'
    # ]
    # urls_list.append(urls)
    #
    # # 17 Mac
    # urls = [
    #     # 1
    #     'https://www.amazon.eg/s?i=videogames&bbn=18022561031&rh=n%3A18022560031%2Cn%3A21868819031&dc&fs=true&language=en&ds=v1%3AdSC9Dc1ptoM%2F7dgN6iRw1DX6jc0jbIGkZJkP1RzS%2BUQ&qid=1684595918&rnid=18022561031&ref=sr_nr_n_3'
    #     ,'https://www.amazon.eg/-/en/s?i=videogames&bbn=18022561031&rh=n%3A18022560031%2Cn%3A21868819031&dc&fs=true&page=2&language=en&qid=1684595921&rnid=18022561031&ref=sr_pg_2'
    #     ,'https://www.amazon.eg/-/en/s?i=videogames&bbn=18022561031&rh=n%3A18022560031%2Cn%3A21868819031&dc&fs=true&page=3&language=en&qid=1684595925&rnid=18022561031&ref=sr_pg_3'
    #     ,'https://www.amazon.eg/-/en/s?i=videogames&bbn=18022561031&rh=n%3A18022560031%2Cn%3A21868819031&dc&fs=true&page=4&language=en&qid=1684595975&rnid=18022561031&ref=sr_pg_4'
    #     ,'https://www.amazon.eg/-/en/s?i=videogames&bbn=18022561031&rh=n%3A18022560031%2Cn%3A21868819031&dc&fs=true&page=5&language=en&qid=1684595984&rnid=18022561031&ref=sr_pg_5'
    #     # 6
    #     ,'https://www.amazon.eg/-/en/s?i=videogames&bbn=18022561031&rh=n%3A18022560031%2Cn%3A21868819031&dc&fs=true&page=6&language=en&qid=1684595994&rnid=18022561031&ref=sr_pg_6'
    #     ,'https://www.amazon.eg/-/en/s?i=videogames&bbn=18022561031&rh=n%3A18022560031%2Cn%3A21868819031&dc&fs=true&page=7&language=en&qid=1684596002&rnid=18022561031&ref=sr_pg_7'
    #     ,'https://www.amazon.eg/-/en/s?i=videogames&bbn=18022561031&rh=n%3A18022560031%2Cn%3A21868819031&dc&fs=true&page=8&language=en&qid=1684596011&rnid=18022561031&ref=sr_pg_8'
    #     ,'https://www.amazon.eg/-/en/s?i=videogames&bbn=18022561031&rh=n%3A18022560031%2Cn%3A21868819031&dc&fs=true&page=9&language=en&qid=1684596026&rnid=18022561031&ref=sr_pg_9'
    #     ,'https://www.amazon.eg/-/en/s?i=videogames&bbn=18022561031&rh=n%3A18022560031%2Cn%3A21868819031&dc&fs=true&page=10&language=en&qid=1684596037&rnid=18022561031&ref=sr_pg_10'
    #     # 11
    #      ,'https://www.amazon.eg/-/en/s?i=videogames&bbn=18022561031&rh=n%3A18022560031%2Cn%3A21868819031&dc&fs=true&page=11&language=en&qid=1684596045&rnid=18022561031&ref=sr_pg_11'
    #      ,'https://www.amazon.eg/-/en/s?i=videogames&bbn=18022561031&rh=n%3A18022560031%2Cn%3A21868819031&dc&fs=true&page=12&language=en&qid=1684596079&rnid=18022561031&ref=sr_pg_12'
    #      ,'https://www.amazon.eg/-/en/s?i=videogames&bbn=18022561031&rh=n%3A18022560031%2Cn%3A21868819031&dc&fs=true&page=13&language=en&qid=1684596103&rnid=18022561031&ref=sr_pg_13'
    #      ,'https://www.amazon.eg/-/en/s?i=videogames&bbn=18022561031&rh=n%3A18022560031%2Cn%3A21868819031&dc&fs=true&page=14&language=en&qid=1684596111&rnid=18022561031&ref=sr_pg_14'
    #      ,'https://www.amazon.eg/-/en/s?i=videogames&bbn=18022561031&rh=n%3A18022560031%2Cn%3A21868819031&dc&fs=true&page=15&language=en&qid=1684596121&rnid=18022561031&ref=sr_pg_15'
    # ]
    # urls_list.append(urls)
    #
    # # 18 Nintendo Switch
    # urls = [
    #     # 1
    #     'https://www.amazon.eg/s?i=videogames&bbn=18022561031&rh=n%3A18022560031%2Cn%3A21868826031&dc&fs=true&language=en&ds=v1%3A5eu96svVMZDX6aLhb8quhYRA2OCuhEvW1vKaac%2BangY&qid=1684596141&rnid=18022561031&ref=sr_nr_n_4'
    #     ,'https://www.amazon.eg/-/en/s?i=videogames&bbn=18022561031&rh=n%3A18022560031%2Cn%3A21868826031&dc&fs=true&page=2&language=en&qid=1684596144&rnid=18022561031&ref=sr_pg_2'
    #     ,'https://www.amazon.eg/-/en/s?i=videogames&bbn=18022561031&rh=n%3A18022560031%2Cn%3A21868826031&dc&fs=true&page=3&language=en&qid=1684596165&rnid=18022561031&ref=sr_pg_3'
    #     ,'https://www.amazon.eg/-/en/s?i=videogames&bbn=18022561031&rh=n%3A18022560031%2Cn%3A21868826031&dc&fs=true&page=4&language=en&qid=1684596173&rnid=18022561031&ref=sr_pg_4'
    #     ,'https://www.amazon.eg/-/en/s?i=videogames&bbn=18022561031&rh=n%3A18022560031%2Cn%3A21868826031&dc&fs=true&page=5&language=en&qid=1684596181&rnid=18022561031&ref=sr_pg_5'
    #     # 6
    #     ,'https://www.amazon.eg/-/en/s?i=videogames&bbn=18022561031&rh=n%3A18022560031%2Cn%3A21868826031&dc&fs=true&page=6&language=en&qid=1684596192&rnid=18022561031&ref=sr_pg_6'
    #     ,'https://www.amazon.eg/-/en/s?i=videogames&bbn=18022561031&rh=n%3A18022560031%2Cn%3A21868826031&dc&fs=true&page=7&language=en&qid=1684596204&rnid=18022561031&ref=sr_pg_7'
    #     ,'https://www.amazon.eg/-/en/s?i=videogames&bbn=18022561031&rh=n%3A18022560031%2Cn%3A21868826031&dc&fs=true&page=8&language=en&qid=1684596273&rnid=18022561031&ref=sr_pg_8'
    #     ,'https://www.amazon.eg/-/en/s?i=videogames&bbn=18022561031&rh=n%3A18022560031%2Cn%3A21868826031&dc&fs=true&page=9&language=en&qid=1684596292&rnid=18022561031&ref=sr_pg_9'
    #     ,'https://www.amazon.eg/-/en/s?i=videogames&bbn=18022561031&rh=n%3A18022560031%2Cn%3A21868826031&dc&fs=true&page=10&language=en&qid=1684596316&rnid=18022561031&ref=sr_pg_10'
    #     # 11
    #     ,'https://www.amazon.eg/-/en/s?i=videogames&bbn=18022561031&rh=n%3A18022560031%2Cn%3A21868826031&dc&fs=true&page=11&language=en&qid=1684596355&rnid=18022561031&ref=sr_pg_11'
    #     ,'https://www.amazon.eg/-/en/s?i=videogames&bbn=18022561031&rh=n%3A18022560031%2Cn%3A21868826031&dc&fs=true&page=12&language=en&qid=1684596364&rnid=18022561031&ref=sr_pg_12'
    #     ,'https://www.amazon.eg/-/en/s?i=videogames&bbn=18022561031&rh=n%3A18022560031%2Cn%3A21868826031&dc&fs=true&page=13&language=en&qid=1684596354&rnid=18022561031&ref=sr_pg_13'
    #     ,'https://www.amazon.eg/-/en/s?i=videogames&bbn=18022561031&rh=n%3A18022560031%2Cn%3A21868826031&dc&fs=true&page=14&language=en&qid=1684596392&rnid=18022561031&ref=sr_pg_14'
    #     ,'https://www.amazon.eg/-/en/s?i=videogames&bbn=18022561031&rh=n%3A18022560031%2Cn%3A21868826031&dc&fs=true&page=15&language=en&qid=1684596404&rnid=18022561031&ref=sr_pg_15'
    # ]
    # urls_list.append(urls)

    # 19 PC
    # urls = [
        # 1
        # 'https://www.amazon.eg/s?i=videogames&bbn=18022561031&rh=n%3A18022560031%2Cn%3A21868814031&dc&fs=true&language=en&ds=v1%3ANnHsOzmKfG%2FEs5UByxuhUVQguaUk2dLPlKKRhHbSo7A&qid=1684596482&rnid=18022561031&ref=sr_nr_n_5'
        # ,'https://www.amazon.eg/-/en/s?i=videogames&bbn=18022561031&rh=n%3A18022560031%2Cn%3A21868814031&dc&fs=true&page=2&language=en&qid=1684596495&rnid=18022561031&ref=sr_pg_2'
        # ,'https://www.amazon.eg/-/en/s?i=videogames&bbn=18022561031&rh=n%3A18022560031%2Cn%3A21868814031&dc&fs=true&page=3&language=en&qid=1684596514&rnid=18022561031&ref=sr_pg_3'
        # ,'https://www.amazon.eg/-/en/s?i=videogames&bbn=18022561031&rh=n%3A18022560031%2Cn%3A21868814031&dc&fs=true&page=4&language=en&qid=1684596522&rnid=18022561031&ref=sr_pg_4'
        # ,'https://www.amazon.eg/-/en/s?i=videogames&bbn=18022561031&rh=n%3A18022560031%2Cn%3A21868814031&dc&fs=true&page=5&language=en&qid=1684596531&rnid=18022561031&ref=sr_pg_5'
        # # 6
        # ,'https://www.amazon.eg/-/en/s?i=videogames&bbn=18022561031&rh=n%3A18022560031%2Cn%3A21868814031&dc&fs=true&page=6&language=en&qid=1684596538&rnid=18022561031&ref=sr_pg_6'
        # ,'https://www.amazon.eg/-/en/s?i=videogames&bbn=18022561031&rh=n%3A18022560031%2Cn%3A21868814031&dc&fs=true&page=7&language=en&qid=1684596547&rnid=18022561031&ref=sr_pg_7'
        # ,'https://www.amazon.eg/-/en/s?i=videogames&bbn=18022561031&rh=n%3A18022560031%2Cn%3A21868814031&dc&fs=true&page=8&language=en&qid=1684596555&rnid=18022561031&ref=sr_pg_8'
        # ,'https://www.amazon.eg/-/en/s?i=videogames&bbn=18022561031&rh=n%3A18022560031%2Cn%3A21868814031&dc&fs=true&page=9&language=en&qid=1684596566&rnid=18022561031&ref=sr_pg_9'
        # ,'https://www.amazon.eg/-/en/s?i=videogames&bbn=18022561031&rh=n%3A18022560031%2Cn%3A21868814031&dc&fs=true&page=10&language=en&qid=1684596573&rnid=18022561031&ref=sr_pg_10'
        # # 11
        # ,'https://www.amazon.eg/-/en/s?i=videogames&bbn=18022561031&rh=n%3A18022560031%2Cn%3A21868814031&dc&fs=true&page=11&language=en&qid=1684596591&rnid=18022561031&ref=sr_pg_11'
        # ,'https://www.amazon.eg/-/en/s?i=videogames&bbn=18022561031&rh=n%3A18022560031%2Cn%3A21868814031&dc&fs=true&page=12&language=en&qid=1684596599&rnid=18022561031&ref=sr_pg_12'
    #     'https://www.amazon.eg/-/en/s?i=videogames&bbn=18022561031&rh=n%3A18022560031%2Cn%3A21868814031&dc&fs=true&page=13&language=en&qid=1684596614&rnid=18022561031&ref=sr_pg_13'
    #     ,'https://www.amazon.eg/-/en/s?i=videogames&bbn=18022561031&rh=n%3A18022560031%2Cn%3A21868814031&dc&fs=true&page=14&language=en&qid=1684596622&rnid=18022561031&ref=sr_pg_14'
    #     ,'https://www.amazon.eg/-/en/s?i=videogames&bbn=18022561031&rh=n%3A18022560031%2Cn%3A21868814031&dc&fs=true&page=15&language=en&qid=1684596631&rnid=18022561031&ref=sr_pg_15'
    # ]
    # urls_list.append(urls)

    # 20 PlayStation 4
    urls = [
        # 1
        # 'https://www.amazon.eg/s?i=videogames&bbn=18022561031&rh=n%3A18022560031%2Cn%3A21868821031&dc&fs=true&language=en&ds=v1%3ABPHF1V0%2FWdCRWzA3q%2B%2BzFW%2FUqFGs9wUUT8RI5OkOKA8&qid=1684598860&rnid=18022561031&ref=sr_nr_n_6'
        # ,'https://www.amazon.eg/-/en/s?i=videogames&bbn=18022561031&rh=n%3A18022560031%2Cn%3A21868821031&dc&fs=true&page=2&language=en&qid=1684598863&rnid=18022561031&ref=sr_pg_2'
        # , 'https://www.amazon.eg/-/en/s?i=videogames&bbn=18022561031&rh=n%3A18022560031%2Cn%3A21868821031&dc&fs=true&page=3&language=en&qid=1684598940&rnid=18022561031&ref=sr_pg_3'
        # , 'https://www.amazon.eg/-/en/s?i=videogames&bbn=18022561031&rh=n%3A18022560031%2Cn%3A21868821031&dc&fs=true&page=4&language=en&qid=1684598942&rnid=18022561031&ref=sr_pg_4'
        # , 'https://www.amazon.eg/-/en/s?i=videogames&bbn=18022561031&rh=n%3A18022560031%2Cn%3A21868821031&dc&fs=true&page=5&language=en&qid=1684598954&rnid=18022561031&ref=sr_pg_5'
        # 6
        # , 'https://www.amazon.eg/-/en/s?i=videogames&bbn=18022561031&rh=n%3A18022560031%2Cn%3A21868821031&dc&fs=true&page=6&language=en&qid=1684598963&rnid=18022561031&ref=sr_pg_6'
        # ,
        'https://www.amazon.eg/-/en/s?i=videogames&bbn=18022561031&rh=n%3A18022560031%2Cn%3A21868821031&dc&fs=true&page=7&language=en&qid=1684598971&rnid=18022561031&ref=sr_pg_7'
        , 'https://www.amazon.eg/-/en/s?i=videogames&bbn=18022561031&rh=n%3A18022560031%2Cn%3A21868821031&dc&fs=true&page=8&language=en&qid=1684598997&rnid=18022561031&ref=sr_pg_8'
        , 'https://www.amazon.eg/-/en/s?i=videogames&bbn=18022561031&rh=n%3A18022560031%2Cn%3A21868821031&dc&fs=true&page=9&language=en&qid=1684599001&rnid=18022561031&ref=sr_pg_9'
        , 'https://www.amazon.eg/-/en/s?i=videogames&bbn=18022561031&rh=n%3A18022560031%2Cn%3A21868821031&dc&fs=true&page=10&language=en&qid=1684599026&rnid=18022561031&ref=sr_pg_10'
        # 11
        , 'https://www.amazon.eg/-/en/s?i=videogames&bbn=18022561031&rh=n%3A18022560031%2Cn%3A21868821031&dc&fs=true&page=11&language=en&qid=1684599037&rnid=18022561031&ref=sr_pg_11'
        , 'https://www.amazon.eg/-/en/s?i=videogames&bbn=18022561031&rh=n%3A18022560031%2Cn%3A21868821031&dc&fs=true&page=12&language=en&qid=1684599047&rnid=18022561031&ref=sr_pg_12'
        , 'https://www.amazon.eg/-/en/s?i=videogames&bbn=18022561031&rh=n%3A18022560031%2Cn%3A21868821031&dc&fs=true&page=13&language=en&qid=1684599058&rnid=18022561031&ref=sr_pg_13'
        # , 'https://www.amazon.eg/-/en/s?i=videogames&bbn=18022561031&rh=n%3A18022560031%2Cn%3A21868821031&dc&fs=true&page=14&language=en&qid=1684599068&rnid=18022561031&ref=sr_pg_14'
        # , 'https://www.amazon.eg/-/en/s?i=videogames&bbn=18022561031&rh=n%3A18022560031%2Cn%3A21868821031&dc&fs=true&page=15&language=en&qid=1684599079&rnid=18022561031&ref=sr_pg_15'
    ]
    urls_list.append(urls)

    # 21 Xbox 360
    urls = [
        # 1
        'https://www.amazon.eg/s?i=videogames&bbn=18022561031&rh=n%3A18022560031%2Cn%3A21868812031&dc&fs=true&language=en&ds=v1%3A%2FiqyvM6%2FNsJEpaS1v4dnUUMa3AbskZfCu12uIACFTpc&qid=1684599113&rnid=18022561031&ref=sr_nr_n_7'
        ,'https://www.amazon.eg/-/en/s?i=videogames&bbn=18022561031&rh=n%3A18022560031%2Cn%3A21868812031&dc&fs=true&page=2&language=en&qid=1684599116&rnid=18022561031&ref=sr_pg_2'
        ,'https://www.amazon.eg/-/en/s?i=videogames&bbn=18022561031&rh=n%3A18022560031%2Cn%3A21868812031&dc&fs=true&page=3&language=en&qid=1684599125&rnid=18022561031&ref=sr_pg_3'
        ,'https://www.amazon.eg/-/en/s?i=videogames&bbn=18022561031&rh=n%3A18022560031%2Cn%3A21868812031&dc&fs=true&page=4&language=en&qid=1684599136&rnid=18022561031&ref=sr_pg_4'
        ,'https://www.amazon.eg/-/en/s?i=videogames&bbn=18022561031&rh=n%3A18022560031%2Cn%3A21868812031&dc&fs=true&page=5&language=en&qid=1684599144&rnid=18022561031&ref=sr_pg_5'
        # 6
        ,'https://www.amazon.eg/-/en/s?i=videogames&bbn=18022561031&rh=n%3A18022560031%2Cn%3A21868812031&dc&fs=true&page=6&language=en&qid=1684599154&rnid=18022561031&ref=sr_pg_6'
        ,'https://www.amazon.eg/-/en/s?i=videogames&bbn=18022561031&rh=n%3A18022560031%2Cn%3A21868812031&dc&fs=true&page=7&language=en&qid=1684599162&rnid=18022561031&ref=sr_pg_7'
        ,'https://www.amazon.eg/-/en/s?i=videogames&bbn=18022561031&rh=n%3A18022560031%2Cn%3A21868812031&dc&fs=true&page=8&language=en&qid=1684599247&rnid=18022561031&ref=sr_pg_8'
        ,'https://www.amazon.eg/-/en/s?i=videogames&bbn=18022561031&rh=n%3A18022560031%2Cn%3A21868812031&dc&fs=true&page=9&language=en&qid=1684599255&rnid=18022561031&ref=sr_pg_9'
        ,'https://www.amazon.eg/-/en/s?i=videogames&bbn=18022561031&rh=n%3A18022560031%2Cn%3A21868812031&dc&fs=true&page=10&language=en&qid=1684599264&rnid=18022561031&ref=sr_pg_10'
        # 11
        ,'https://www.amazon.eg/-/en/s?i=videogames&bbn=18022561031&rh=n%3A18022560031%2Cn%3A21868812031&dc&fs=true&page=11&language=en&qid=1684599289&rnid=18022561031&ref=sr_pg_11'
        ,'https://www.amazon.eg/-/en/s?i=videogames&bbn=18022561031&rh=n%3A18022560031%2Cn%3A21868812031&dc&fs=true&page=12&language=en&qid=1684599306&rnid=18022561031&ref=sr_pg_12'
        ,'https://www.amazon.eg/-/en/s?i=videogames&bbn=18022561031&rh=n%3A18022560031%2Cn%3A21868812031&dc&fs=true&page=13&language=en&qid=1684599314&rnid=18022561031&ref=sr_pg_13'
        ,'https://www.amazon.eg/-/en/s?i=videogames&bbn=18022561031&rh=n%3A18022560031%2Cn%3A21868812031&dc&fs=true&page=14&language=en&qid=1684599321&rnid=18022561031&ref=sr_pg_14'
        ,'https://www.amazon.eg/-/en/s?i=videogames&bbn=18022561031&rh=n%3A18022560031%2Cn%3A21868812031&dc&fs=true&page=15&language=en&qid=1684599334&rnid=18022561031&ref=sr_pg_15'
        ,'https://www.amazon.eg/-/en/s?i=videogames&bbn=18022561031&rh=n%3A18022560031%2Cn%3A21868812031&dc&fs=true&page=16&language=en&qid=1684656902&rnid=18022561031&ref=sr_pg_16'
        ,'https://www.amazon.eg/-/en/s?i=videogames&bbn=18022561031&rh=n%3A18022560031%2Cn%3A21868812031&dc&fs=true&page=17&language=en&qid=1684656905&rnid=18022561031&ref=sr_pg_17'
    ]
    urls_list.append(urls)

    # 22 Xbox One
    urls = [
        # 1
        'https://www.amazon.eg/s?i=videogames&bbn=18022561031&rh=n%3A18022560031%2Cn%3A21868820031&dc&fs=true&language=en&ds=v1%3AvaXSevV%2FgxlYW4iUXThJStEvHSM91UNVS6VwZeJ6a98&qid=1684599352&rnid=18022561031&ref=sr_nr_n_8'
        ,'https://www.amazon.eg/-/en/s?i=videogames&bbn=18022561031&rh=n%3A18022560031%2Cn%3A21868820031&dc&fs=true&page=2&language=en&qid=1684599355&rnid=18022561031&ref=sr_pg_2'
        ,'https://www.amazon.eg/-/en/s?i=videogames&bbn=18022561031&rh=n%3A18022560031%2Cn%3A21868820031&dc&fs=true&page=3&language=en&qid=1684599358&rnid=18022561031&ref=sr_pg_3'
        ,'https://www.amazon.eg/-/en/s?i=videogames&bbn=18022561031&rh=n%3A18022560031%2Cn%3A21868820031&dc&fs=true&page=4&language=en&qid=1684599374&rnid=18022561031&ref=sr_pg_4'
        ,'https://www.amazon.eg/-/en/s?i=videogames&bbn=18022561031&rh=n%3A18022560031%2Cn%3A21868820031&dc&fs=true&page=5&language=en&qid=1684599389&rnid=18022561031&ref=sr_pg_5'
        # 6
        ,'https://www.amazon.eg/-/en/s?i=videogames&bbn=18022561031&rh=n%3A18022560031%2Cn%3A21868820031&dc&fs=true&page=6&language=en&qid=1684599402&rnid=18022561031&ref=sr_pg_6'
        ,'https://www.amazon.eg/-/en/s?i=videogames&bbn=18022561031&rh=n%3A18022560031%2Cn%3A21868820031&dc&fs=true&page=7&language=en&qid=1684599418&rnid=18022561031&ref=sr_pg_7'
        ,'https://www.amazon.eg/-/en/s?i=videogames&bbn=18022561031&rh=n%3A18022560031%2Cn%3A21868820031&dc&fs=true&page=8&language=en&qid=1684599433&rnid=18022561031&ref=sr_pg_8'
        ,'https://www.amazon.eg/-/en/s?i=videogames&bbn=18022561031&rh=n%3A18022560031%2Cn%3A21868820031&dc&fs=true&page=9&language=en&qid=1684599441&rnid=18022561031&ref=sr_pg_9'
        ,'https://www.amazon.eg/-/en/s?i=videogames&bbn=18022561031&rh=n%3A18022560031%2Cn%3A21868820031&dc&fs=true&page=10&language=en&qid=1684599450&rnid=18022561031&ref=sr_pg_10'
        # 11
         ,'https://www.amazon.eg/-/en/s?i=videogames&bbn=18022561031&rh=n%3A18022560031%2Cn%3A21868820031&dc&fs=true&page=11&language=en&qid=1684599457&rnid=18022561031&ref=sr_pg_11'
         ,'https://www.amazon.eg/-/en/s?i=videogames&bbn=18022561031&rh=n%3A18022560031%2Cn%3A21868820031&dc&fs=true&page=12&language=en&qid=1684599464&rnid=18022561031&ref=sr_pg_12'
         ,'https://www.amazon.eg/-/en/s?i=videogames&bbn=18022561031&rh=n%3A18022560031%2Cn%3A21868820031&dc&fs=true&page=13&language=en&qid=1684599472&rnid=18022561031&ref=sr_pg_13'
         ,'https://www.amazon.eg/-/en/s?i=videogames&bbn=18022561031&rh=n%3A18022560031%2Cn%3A21868820031&dc&fs=true&page=14&language=en&qid=1684599478&rnid=18022561031&ref=sr_pg_14'
         ,'https://www.amazon.eg/-/en/s?i=videogames&bbn=18022561031&rh=n%3A18022560031%2Cn%3A21868820031&dc&fs=true&page=15&language=en&qid=1684599484&rnid=18022561031&ref=sr_pg_15'
    ]
    urls_list.append(urls)

    cat_id = 20
    start_id = 1672
    
    for urls_list_index in range(0, len(urls_list)):
        end_id = start_id + 200
        if cat_id == 20:
            end_id = 1547 + 200
        print('目前為', str(cat_id), '類 的資料--------------------------------------StartId:', str(start_id))
        if start_id >= end_id:
            print('目前為', str(cat_id), '類 的資料-----------------------------------StartId:', str(start_id))
            print('已打印完', str(start_id), '提早結束(' + str(end_id) + ')')
            print('提早結束完成', str(cat_id), '類')
            return
        for url_num_Index in range(0, len(urls_list[urls_list_index])):
            if start_id >= end_id:
                print('目前為', str(cat_id), '類 的資料-----------------------------------StartId:', str(start_id))
                print('已打印完', str(start_id), '提早結束('+str(end_id)+')')
                print('已打印完', str(start_id), '提早結束('+str(end_id)+')')
                break
            time.sleep(0.2)
            print('目前為', str(cat_id), '類 的資料-----------------------------------StartId:', str(start_id))
            print('目前為', str(cat_id), '類 的資料-----------------------------------StartId:', str(start_id))
            print('目前為', str(cat_id), '類 的資料-----------------------------------StartId:', str(start_id))
            print('目前為', str(cat_id), '類 的資料-----------------------------------StartId:', str(start_id))
            print(str(cat_id) + '類 開始' + str(url_num_Index+1) + '頁--------------------------------------------------')
            print(str(cat_id) + '類 開始' + str(url_num_Index+1) + '頁--------------------------------------------------')
            print(str(cat_id) + '類 開始' + str(url_num_Index+1) + '頁--------------------------------------------------')
            print(str(cat_id) + '類 開始' + str(url_num_Index+1) + '頁--------------------------------------------------')
            start_id = await product_list_web_crawler(urls_list[urls_list_index][url_num_Index], start_id, cat_id)
            print('目前打印完' + str(cat_id) + '類' + str(url_num_Index+1) + '頁，共', start_id, '筆')
            print('目前打印完' + str(cat_id) + '類' + str(url_num_Index+1) + '頁，共', start_id, '筆')
            print('目前打印完' + str(cat_id) + '類' + str(url_num_Index+1) + '頁，共', start_id, '筆')
            print('目前打印完' + str(cat_id) + '類' + str(url_num_Index+1) + '頁，共', start_id, '筆')
            print('目前為', str(cat_id), '類 的資料-----------------------------------StartId:', str(start_id))
            print('目前為', str(cat_id), '類 的資料-----------------------------------StartId:', str(start_id))
            print('目前為', str(cat_id), '類 的資料-----------------------------------StartId:', str(start_id))
        cat_id += 1

    # 取網頁網址
    # url = 'https://www.amazon.eg/s?i=videogames&bbn=18022561031&rh=n%3A18022560031%2Cn%3A21868820031&dc&fs=true&language=en&ds=v1%3AcIiKnYg%2BrkRnw3WnvAkzH%2FDZ93%2Bl6C00W4yJYsz8d1o&qid=1684598682&rnid=18022561031&ref=sr_nr_n_8'
    # pages = 15
    # await get_pagesUrl(url, pages)

    ## 取分類表
    # 取分類網址
    # url = 'https://www.amazon.eg/s?rh=n%3A18022560031&fs=true&language=en&ref=lp_18022560031_sar'
    # cat_id = 14
    # parent_id = 14
    # sort = 14
    # await get_categories(url, cat_id, parent_id, sort)

    print('完成')




asyncio.run(main())
