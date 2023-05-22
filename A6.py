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


async def web_crawler_with_selenium(url,try_count = 0, isProductDetail = True):
    try:
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

        waitTime = 0.2 if isProductDetail else 0
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
        try_count = 0
    except Exception as e:
        try_count += 1
        print("發生異常:", url, '，重試', str(try_count), '次')
        print("發生異常:", e)
        if try_count < 3:
            return await web_crawler_with_selenium(url, try_count, isProductDetail)
        else:
            raise Exception("重試次數已達上限，無法繼續執行") from e

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
    name_index = 0
    for product_name in product_names:
        productnames_array.append(product_name.text.strip())
        print(product_name.text.strip())
        id_array.append(start_id)
        if '🇺🇸' in product_name.text.strip():
            skipItem.append(name_index)
        start_id += 1
        name_index += 1

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
    thumbnail_elements = soup.select('.s-card-container .s-product-image-container .s-image')
    thumbnail_index = 0
    for thumbnail_element in thumbnail_elements:
        thumbnail_url = thumbnail_element.get('src', None)
        thumb_img_array.append(remove_number_from_url(thumbnail_url))
        print(thumbnail_index, '---:', thumbnail_url)
        thumbnail_index += 1


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
    print("'" + url + "',")

    html = await fetch_url(url)
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.select('.s-pagination-container a')
    url = 'https://www.amazon.eg' + items[0]['href']
    # 2
    print("'" + url + "',")
    url = 'https://www.amazon.eg' + items[1]['href']
    # 3
    print("'" + url + "',")
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
            if pageCount == pages:
                print("'" + url + "'")
            else:
                print("'" + url + "',")

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
    # 24 Bath & Body
    # urls = [
    #     # 1
    #     'https://www.amazon.eg/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826027031&dc&fs=true&language=en&ds=v1%3AwxBWLCSdJGIBpyFcoqxaCjZOCSDeCPE6Iu3obGpkG%2Bs&qid=1684664965&rnid=18017989031&ref=sr_nr_n_1',
    #     'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826027031&dc&fs=true&page=2&language=en&qid=1684666147&rnid=18017989031&ref=sr_pg_2',
    #     'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826027031&dc&fs=true&page=3&language=en&qid=1684666147&rnid=18017989031&ref=sr_pg_3',
    #     'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826027031&dc&fs=true&page=4&language=en&qid=1684666149&rnid=18017989031&ref=sr_pg_4',
    #     'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826027031&dc&fs=true&page=5&language=en&qid=1684666151&rnid=18017989031&ref=sr_pg_5',
    #     # 6
    #     'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826027031&dc&fs=true&page=6&language=en&qid=1684666153&rnid=18017989031&ref=sr_pg_5',
    #     'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826027031&dc&fs=true&page=7&language=en&qid=1684666155&rnid=18017989031&ref=sr_pg_6',
    #     'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826027031&dc&fs=true&page=8&language=en&qid=1684666157&rnid=18017989031&ref=sr_pg_7',
    #     'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826027031&dc&fs=true&page=9&language=en&qid=1684666159&rnid=18017989031&ref=sr_pg_8',
    #     'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826027031&dc&fs=true&page=10&language=en&qid=1684666161&rnid=18017989031&ref=sr_pg_9',
    #     # 11
    #     'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826027031&dc&fs=true&page=11&language=en&qid=1684666163&rnid=18017989031&ref=sr_pg_10',
    #     'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826027031&dc&fs=true&page=12&language=en&qid=1684666165&rnid=18017989031&ref=sr_pg_11',
    #     'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826027031&dc&fs=true&page=13&language=en&qid=1684666167&rnid=18017989031&ref=sr_pg_12',
    #     'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826027031&dc&fs=true&page=14&language=en&qid=1684666169&rnid=18017989031&ref=sr_pg_13',
    #     'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826027031&dc&fs=true&page=15&language=en&qid=1684666171&rnid=18017989031&ref=sr_pg_14',
    #     # 16
    #     'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826027031&dc&fs=true&page=16&language=en&qid=1684666173&rnid=18017989031&ref=sr_pg_15',
    #     'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826027031&dc&fs=true&page=17&language=en&qid=1684666175&rnid=18017989031&ref=sr_pg_16',
    #     'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826027031&dc&fs=true&page=18&language=en&qid=1684666177&rnid=18017989031&ref=sr_pg_17',
    #     'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826027031&dc&fs=true&page=19&language=en&qid=1684666179&rnid=18017989031&ref=sr_pg_18',
    #     'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826027031&dc&fs=true&page=20&language=en&qid=1684666181&rnid=18017989031&ref=sr_pg_19'
    # ]
    # urls_list.append(urls)

    # 25 Fragrances
    # urls = [
    #     # 1
    #     'https://www.amazon.eg/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826026031&dc&fs=true&language=en&ds=v1%3AW6YcdFlxjyw4OnHTQuMjyPraJoUV8bHZ0sGbek9GyF0&qid=1684666320&rnid=18017989031&ref=sr_nr_n_2',
    #     'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826026031&dc&fs=true&page=2&language=en&qid=1684666335&rnid=18017989031&ref=sr_pg_2',
    #     'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826026031&dc&fs=true&page=3&language=en&qid=1684666335&rnid=18017989031&ref=sr_pg_3',
    #     'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826026031&dc&fs=true&page=4&language=en&qid=1684666337&rnid=18017989031&ref=sr_pg_4',
    #     'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826026031&dc&fs=true&page=5&language=en&qid=1684666339&rnid=18017989031&ref=sr_pg_5',
    #     # 6
    #     'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826026031&dc&fs=true&page=6&language=en&qid=1684666341&rnid=18017989031&ref=sr_pg_5',
    #     'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826026031&dc&fs=true&page=7&language=en&qid=1684666343&rnid=18017989031&ref=sr_pg_6',
    #     'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826026031&dc&fs=true&page=8&language=en&qid=1684666345&rnid=18017989031&ref=sr_pg_7',
    #     'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826026031&dc&fs=true&page=9&language=en&qid=1684666347&rnid=18017989031&ref=sr_pg_8',
    #     'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826026031&dc&fs=true&page=10&language=en&qid=1684666350&rnid=18017989031&ref=sr_pg_9',
    #     # 11
    #     'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826026031&dc&fs=true&page=11&language=en&qid=1684666352&rnid=18017989031&ref=sr_pg_10',
    #     'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826026031&dc&fs=true&page=12&language=en&qid=1684666354&rnid=18017989031&ref=sr_pg_11',
    #     'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826026031&dc&fs=true&page=13&language=en&qid=1684666356&rnid=18017989031&ref=sr_pg_12',
    #     'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826026031&dc&fs=true&page=14&language=en&qid=1684666358&rnid=18017989031&ref=sr_pg_13',
    #     'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826026031&dc&fs=true&page=15&language=en&qid=1684666360&rnid=18017989031&ref=sr_pg_14',
    #     # 16
    #     'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826026031&dc&fs=true&page=16&language=en&qid=1684666361&rnid=18017989031&ref=sr_pg_15',
    #     'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826026031&dc&fs=true&page=17&language=en&qid=1684666363&rnid=18017989031&ref=sr_pg_16',
    #     'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826026031&dc&fs=true&page=18&language=en&qid=1684666365&rnid=18017989031&ref=sr_pg_17',
    #     'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826026031&dc&fs=true&page=19&language=en&qid=1684666367&rnid=18017989031&ref=sr_pg_18',
    #     'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826026031&dc&fs=true&page=20&language=en&qid=1684666370&rnid=18017989031&ref=sr_pg_19'
    # ]
    # urls_list.append(urls)

    # 26 Hair Care 2507
    urls = [
        # 1
        'https://www.amazon.eg/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826029031&dc&fs=true&language=en&ds=v1%3A3Fak%2FJBtDDO22PcAbuGpvuGNb5WhYW1xiwVRUcUz1MU&qid=1684666347&rnid=18017989031&ref=sr_nr_n_3',
        'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826029031&dc&fs=true&page=2&language=en&qid=1684666431&rnid=18017989031&ref=sr_pg_2',
        'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826029031&dc&fs=true&page=3&language=en&qid=1684666431&rnid=18017989031&ref=sr_pg_3',
        'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826029031&dc&fs=true&page=4&language=en&qid=1684666432&rnid=18017989031&ref=sr_pg_4',
        'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826029031&dc&fs=true&page=5&language=en&qid=1684666436&rnid=18017989031&ref=sr_pg_5',
        # 6
        'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826029031&dc&fs=true&page=6&language=en&qid=1684666438&rnid=18017989031&ref=sr_pg_5',
        'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826029031&dc&fs=true&page=7&language=en&qid=1684666440&rnid=18017989031&ref=sr_pg_6',
        'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826029031&dc&fs=true&page=8&language=en&qid=1684666442&rnid=18017989031&ref=sr_pg_7',
        'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826029031&dc&fs=true&page=9&language=en&qid=1684666444&rnid=18017989031&ref=sr_pg_8',
        'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826029031&dc&fs=true&page=10&language=en&qid=1684666446&rnid=18017989031&ref=sr_pg_9',
        # 11
        'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826029031&dc&fs=true&page=11&language=en&qid=1684666448&rnid=18017989031&ref=sr_pg_10',
        'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826029031&dc&fs=true&page=12&language=en&qid=1684666450&rnid=18017989031&ref=sr_pg_11',
        'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826029031&dc&fs=true&page=13&language=en&qid=1684666452&rnid=18017989031&ref=sr_pg_12',
        'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826029031&dc&fs=true&page=14&language=en&qid=1684666454&rnid=18017989031&ref=sr_pg_13',
        'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826029031&dc&fs=true&page=15&language=en&qid=1684666456&rnid=18017989031&ref=sr_pg_14',
        # 16
        'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826029031&dc&fs=true&page=16&language=en&qid=1684666458&rnid=18017989031&ref=sr_pg_15',
        'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826029031&dc&fs=true&page=17&language=en&qid=1684666460&rnid=18017989031&ref=sr_pg_16',
        'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826029031&dc&fs=true&page=18&language=en&qid=1684666462&rnid=18017989031&ref=sr_pg_17',
        'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826029031&dc&fs=true&page=19&language=en&qid=1684666464&rnid=18017989031&ref=sr_pg_18',
        'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826029031&dc&fs=true&page=20&language=en&qid=1684666465&rnid=18017989031&ref=sr_pg_19'
    ]
    urls_list.append(urls)

    # 27 Makeup
    urls = [
        # 1
        'https://www.amazon.eg/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826032031&dc&fs=true&language=en&ds=v1%3A1MtmPSbIT%2FXS%2F0QDB5FCPsTuV%2Fy4EiSIxuZeYawnLzs&qid=1684666347&rnid=18017989031&ref=sr_nr_n_4',
        'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826032031&dc&fs=true&page=2&language=en&qid=1684666827&rnid=18017989031&ref=sr_pg_2',
        'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826032031&dc&fs=true&page=3&language=en&qid=1684666827&rnid=18017989031&ref=sr_pg_3',
        'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826032031&dc&fs=true&page=4&language=en&qid=1684666828&rnid=18017989031&ref=sr_pg_4',
        'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826032031&dc&fs=true&page=5&language=en&qid=1684666830&rnid=18017989031&ref=sr_pg_5',
        # 6
        'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826032031&dc&fs=true&page=6&language=en&qid=1684666832&rnid=18017989031&ref=sr_pg_5',
        'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826032031&dc&fs=true&page=7&language=en&qid=1684666834&rnid=18017989031&ref=sr_pg_6',
        'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826032031&dc&fs=true&page=8&language=en&qid=1684666836&rnid=18017989031&ref=sr_pg_7',
        'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826032031&dc&fs=true&page=9&language=en&qid=1684666838&rnid=18017989031&ref=sr_pg_8',
        'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826032031&dc&fs=true&page=10&language=en&qid=1684666840&rnid=18017989031&ref=sr_pg_9',
        # 11
        'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826032031&dc&fs=true&page=11&language=en&qid=1684666842&rnid=18017989031&ref=sr_pg_10',
        'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826032031&dc&fs=true&page=12&language=en&qid=1684666844&rnid=18017989031&ref=sr_pg_11',
        'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826032031&dc&fs=true&page=13&language=en&qid=1684666846&rnid=18017989031&ref=sr_pg_12',
        'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826032031&dc&fs=true&page=14&language=en&qid=1684666848&rnid=18017989031&ref=sr_pg_13',
        'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826032031&dc&fs=true&page=15&language=en&qid=1684666850&rnid=18017989031&ref=sr_pg_14',
        # 16
        'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826032031&dc&fs=true&page=16&language=en&qid=1684666852&rnid=18017989031&ref=sr_pg_15',
        'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826032031&dc&fs=true&page=17&language=en&qid=1684666854&rnid=18017989031&ref=sr_pg_16',
        'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826032031&dc&fs=true&page=18&language=en&qid=1684666856&rnid=18017989031&ref=sr_pg_17',
        'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826032031&dc&fs=true&page=19&language=en&qid=1684666857&rnid=18017989031&ref=sr_pg_18',
        'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826032031&dc&fs=true&page=20&language=en&qid=1684666859&rnid=18017989031&ref=sr_pg_19'
    ]
    urls_list.append(urls)

    # 28 Manicure & Pedicure
    urls = [
        #1
        'https://www.amazon.eg/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826024031&dc&fs=true&language=en&ds=v1%3Apn1CSZVUmPGa5gGMB2MD2N1Z8X%2FfjfG3DZzKAdh4bIA&qid=1684666347&rnid=18017989031&ref=sr_nr_n_5',
        'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826024031&dc&fs=true&page=2&language=en&qid=1684666861&rnid=18017989031&ref=sr_pg_2',
        'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826024031&dc&fs=true&page=3&language=en&qid=1684666861&rnid=18017989031&ref=sr_pg_3',
        'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826024031&dc&fs=true&page=4&language=en&qid=1684666863&rnid=18017989031&ref=sr_pg_4',
        'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826024031&dc&fs=true&page=5&language=en&qid=1684666865&rnid=18017989031&ref=sr_pg_5',
        # 6
        'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826024031&dc&fs=true&page=6&language=en&qid=1684666867&rnid=18017989031&ref=sr_pg_5',
        'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826024031&dc&fs=true&page=7&language=en&qid=1684666869&rnid=18017989031&ref=sr_pg_6',
        'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826024031&dc&fs=true&page=8&language=en&qid=1684666871&rnid=18017989031&ref=sr_pg_7',
        'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826024031&dc&fs=true&page=9&language=en&qid=1684666873&rnid=18017989031&ref=sr_pg_8',
        'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826024031&dc&fs=true&page=10&language=en&qid=1684666876&rnid=18017989031&ref=sr_pg_9',
        # 11
        'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826024031&dc&fs=true&page=11&language=en&qid=1684666878&rnid=18017989031&ref=sr_pg_10',
        'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826024031&dc&fs=true&page=12&language=en&qid=1684666880&rnid=18017989031&ref=sr_pg_11',
        'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826024031&dc&fs=true&page=13&language=en&qid=1684666882&rnid=18017989031&ref=sr_pg_12',
        'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826024031&dc&fs=true&page=14&language=en&qid=1684666884&rnid=18017989031&ref=sr_pg_13',
        'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826024031&dc&fs=true&page=15&language=en&qid=1684666885&rnid=18017989031&ref=sr_pg_14',
        # 16
        'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826024031&dc&fs=true&page=16&language=en&qid=1684666887&rnid=18017989031&ref=sr_pg_15',
        'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826024031&dc&fs=true&page=17&language=en&qid=1684666890&rnid=18017989031&ref=sr_pg_16',
        'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826024031&dc&fs=true&page=18&language=en&qid=1684666892&rnid=18017989031&ref=sr_pg_17',
        'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826024031&dc&fs=true&page=19&language=en&qid=1684666894&rnid=18017989031&ref=sr_pg_18',
        'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826024031&dc&fs=true&page=20&language=en&qid=1684666896&rnid=18017989031&ref=sr_pg_19'
    ]
    urls_list.append(urls)

    # 29 Salon & Spa Equipment
    urls = [
        # 1
        'https://www.amazon.eg/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826031031&dc&fs=true&language=en&ds=v1%3ACuHix1K7hsCzlq%2BgDL3Z%2Fji1zBp60qJNQgIV5wddYNA&qid=1684666347&rnid=18017989031&ref=sr_nr_n_6',
        'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826031031&dc&fs=true&page=2&language=en&qid=1684666898&rnid=18017989031&ref=sr_pg_2',
        'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826031031&dc&fs=true&page=3&language=en&qid=1684666898&rnid=18017989031&ref=sr_pg_3',
        'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826031031&dc&fs=true&page=4&language=en&qid=1684666900&rnid=18017989031&ref=sr_pg_4'
    ]
    urls_list.append(urls)

    # 30 Shaving & Hair Removal
    urls = [
        # 1
        'https://www.amazon.eg/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826028031&dc&fs=true&language=en&ds=v1%3AzsKtcEFYJVEZzlN1S09FGt9H5DUsVKszXdEGtUxJO%2F0&qid=1684666347&rnid=18017989031&ref=sr_nr_n_7',
        'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826028031&dc&fs=true&page=2&language=en&qid=1684667437&rnid=18017989031&ref=sr_pg_2',
        'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826028031&dc&fs=true&page=3&language=en&qid=1684667437&rnid=18017989031&ref=sr_pg_3',
        'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826028031&dc&fs=true&page=4&language=en&qid=1684667439&rnid=18017989031&ref=sr_pg_4',
        'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826028031&dc&fs=true&page=5&language=en&qid=1684667441&rnid=18017989031&ref=sr_pg_5',
        # 6
        'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826028031&dc&fs=true&page=6&language=en&qid=1684667443&rnid=18017989031&ref=sr_pg_5',
        'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826028031&dc&fs=true&page=7&language=en&qid=1684667445&rnid=18017989031&ref=sr_pg_6',
        'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826028031&dc&fs=true&page=8&language=en&qid=1684667447&rnid=18017989031&ref=sr_pg_7',
        'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826028031&dc&fs=true&page=9&language=en&qid=1684667449&rnid=18017989031&ref=sr_pg_8',
        'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826028031&dc&fs=true&page=10&language=en&qid=1684667450&rnid=18017989031&ref=sr_pg_9',
        # 11
        'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826028031&dc&fs=true&page=11&language=en&qid=1684667452&rnid=18017989031&ref=sr_pg_10',
        'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826028031&dc&fs=true&page=12&language=en&qid=1684667454&rnid=18017989031&ref=sr_pg_11',
        'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826028031&dc&fs=true&page=13&language=en&qid=1684667456&rnid=18017989031&ref=sr_pg_12',
        'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826028031&dc&fs=true&page=14&language=en&qid=1684667458&rnid=18017989031&ref=sr_pg_13',
        'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826028031&dc&fs=true&page=15&language=en&qid=1684667460&rnid=18017989031&ref=sr_pg_14',
        # 16
        'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826028031&dc&fs=true&page=16&language=en&qid=1684667462&rnid=18017989031&ref=sr_pg_15',
        'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826028031&dc&fs=true&page=17&language=en&qid=1684667463&rnid=18017989031&ref=sr_pg_16',
        'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826028031&dc&fs=true&page=18&language=en&qid=1684667464&rnid=18017989031&ref=sr_pg_17',
        'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826028031&dc&fs=true&page=19&language=en&qid=1684667466&rnid=18017989031&ref=sr_pg_18',
        'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826028031&dc&fs=true&page=20&language=en&qid=1684667468&rnid=18017989031&ref=sr_pg_19'
    ]
    urls_list.append(urls)

    # 31 Skin Care
    urls = [
        # 1
        'https://www.amazon.eg/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826030031&dc&fs=true&language=en&ds=v1%3AgWjJUyc4a4G1ypxlBv4d6OYmqE2fusk9cE6tsKOLD%2BM&qid=1684666347&rnid=18017989031&ref=sr_nr_n_8',
        'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826030031&dc&fs=true&page=2&language=en&qid=1684667470&rnid=18017989031&ref=sr_pg_2',
        'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826030031&dc&fs=true&page=3&language=en&qid=1684667470&rnid=18017989031&ref=sr_pg_3',
        'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826030031&dc&fs=true&page=4&language=en&qid=1684667472&rnid=18017989031&ref=sr_pg_4',
        'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826030031&dc&fs=true&page=5&language=en&qid=1684667474&rnid=18017989031&ref=sr_pg_5',
        # 6
        'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826030031&dc&fs=true&page=6&language=en&qid=1684667476&rnid=18017989031&ref=sr_pg_5',
        'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826030031&dc&fs=true&page=7&language=en&qid=1684667478&rnid=18017989031&ref=sr_pg_6',
        'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826030031&dc&fs=true&page=8&language=en&qid=1684667480&rnid=18017989031&ref=sr_pg_7',
        'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826030031&dc&fs=true&page=9&language=en&qid=1684667482&rnid=18017989031&ref=sr_pg_8',
        'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826030031&dc&fs=true&page=10&language=en&qid=1684667484&rnid=18017989031&ref=sr_pg_9',
        # 11
        'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826030031&dc&fs=true&page=11&language=en&qid=1684667486&rnid=18017989031&ref=sr_pg_10',
        'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826030031&dc&fs=true&page=12&language=en&qid=1684667488&rnid=18017989031&ref=sr_pg_11',
        'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826030031&dc&fs=true&page=13&language=en&qid=1684667490&rnid=18017989031&ref=sr_pg_12',
        'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826030031&dc&fs=true&page=14&language=en&qid=1684667492&rnid=18017989031&ref=sr_pg_13',
        'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826030031&dc&fs=true&page=15&language=en&qid=1684667494&rnid=18017989031&ref=sr_pg_14',
        # 16
        'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826030031&dc&fs=true&page=16&language=en&qid=1684667496&rnid=18017989031&ref=sr_pg_15',
        'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826030031&dc&fs=true&page=17&language=en&qid=1684667498&rnid=18017989031&ref=sr_pg_16',
        'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826030031&dc&fs=true&page=18&language=en&qid=1684667500&rnid=18017989031&ref=sr_pg_17',
        'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826030031&dc&fs=true&page=19&language=en&qid=1684667502&rnid=18017989031&ref=sr_pg_18',
        'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826030031&dc&fs=true&page=20&language=en&qid=1684667504&rnid=18017989031&ref=sr_pg_19'

    ]
    urls_list.append(urls)

    # 32 Tools & Accessories
    urls = [
        # 1
        'https://www.amazon.eg/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826025031&dc&fs=true&language=en&ds=v1%3ATzFw7iq6LUp01FxrKGBQP9famltCKQMNQvonvsPeDHI&qid=1684666347&rnid=18017989031&ref=sr_nr_n_9',
        'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826025031&dc&fs=true&page=2&language=en&qid=1684667506&rnid=18017989031&ref=sr_pg_2',
        'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826025031&dc&fs=true&page=3&language=en&qid=1684667506&rnid=18017989031&ref=sr_pg_3',
        'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826025031&dc&fs=true&page=4&language=en&qid=1684667508&rnid=18017989031&ref=sr_pg_4',
        'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826025031&dc&fs=true&page=5&language=en&qid=1684667510&rnid=18017989031&ref=sr_pg_5',
        # 6
        'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826025031&dc&fs=true&page=6&language=en&qid=1684667512&rnid=18017989031&ref=sr_pg_5',
        'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826025031&dc&fs=true&page=7&language=en&qid=1684667514&rnid=18017989031&ref=sr_pg_6',
        'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826025031&dc&fs=true&page=8&language=en&qid=1684667516&rnid=18017989031&ref=sr_pg_7',
        'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826025031&dc&fs=true&page=9&language=en&qid=1684667518&rnid=18017989031&ref=sr_pg_8',
        'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826025031&dc&fs=true&page=10&language=en&qid=1684667520&rnid=18017989031&ref=sr_pg_9',
        # 11
        'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826025031&dc&fs=true&page=11&language=en&qid=1684667522&rnid=18017989031&ref=sr_pg_10',
        'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826025031&dc&fs=true&page=12&language=en&qid=1684667524&rnid=18017989031&ref=sr_pg_11',
        'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826025031&dc&fs=true&page=13&language=en&qid=1684667526&rnid=18017989031&ref=sr_pg_12',
        'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826025031&dc&fs=true&page=14&language=en&qid=1684667528&rnid=18017989031&ref=sr_pg_13',
        'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826025031&dc&fs=true&page=15&language=en&qid=1684667530&rnid=18017989031&ref=sr_pg_14',
        # 16
        'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826025031&dc&fs=true&page=16&language=en&qid=1684667532&rnid=18017989031&ref=sr_pg_15',
        'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826025031&dc&fs=true&page=17&language=en&qid=1684667534&rnid=18017989031&ref=sr_pg_16',
        'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826025031&dc&fs=true&page=18&language=en&qid=1684667536&rnid=18017989031&ref=sr_pg_17',
        'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826025031&dc&fs=true&page=19&language=en&qid=1684667538&rnid=18017989031&ref=sr_pg_18',
        'https://www.amazon.eg/-/en/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826025031&dc&fs=true&page=20&language=en&qid=1684667540&rnid=18017989031&ref=sr_pg_19'
    ]
    urls_list.append(urls)

    cat_id = 26
    start_id = 2507

    for urls_list_index in range(0, len(urls_list)):
        end_id = start_id + 200
        if cat_id == 24:
            end_id = 2190 + 200
        print('目前為', str(cat_id), '類 的資料--------------------------------------StartId:', str(start_id))
        if start_id >= end_id:
            print('目前為', str(cat_id), '類 的資料-----------------------------------StartId:', str(start_id))
            print('已打印完', str(start_id), '提早結束(' + str(end_id) + ')')
            print('提早結束完成', str(cat_id), '類')
            return
        for url_num_Index in range(0, len(urls_list[urls_list_index])):
            if start_id >= end_id:
                print('目前為', str(cat_id), '類 的資料-----------------------------------StartId:', str(start_id))
                print('已打印完', str(start_id), '提早結束(' + str(end_id) + ')')
                print('已打印完', str(start_id), '提早結束(' + str(end_id) + ')')
                break
            time.sleep(0.2)
            print('目前為', str(cat_id), '類 的資料-----------------------------------StartId:', str(start_id))
            print('目前為', str(cat_id), '類 的資料-----------------------------------StartId:', str(start_id))
            print('目前為', str(cat_id), '類 的資料-----------------------------------StartId:', str(start_id))
            print('目前為', str(cat_id), '類 的資料-----------------------------------StartId:', str(start_id))
            print(str(cat_id) + '類 開始' + str(
                url_num_Index + 1) + '頁--------------------------------------------------')
            print(str(cat_id) + '類 開始' + str(
                url_num_Index + 1) + '頁--------------------------------------------------')
            print(str(cat_id) + '類 開始' + str(
                url_num_Index + 1) + '頁--------------------------------------------------')
            print(str(cat_id) + '類 開始' + str(
                url_num_Index + 1) + '頁--------------------------------------------------')
            start_id = await product_list_web_crawler(urls_list[urls_list_index][url_num_Index], start_id, cat_id)
            print('目前打印完' + str(cat_id) + '類' + str(url_num_Index + 1) + '頁，共', start_id, '筆')
            print('目前打印完' + str(cat_id) + '類' + str(url_num_Index + 1) + '頁，共', start_id, '筆')
            print('目前打印完' + str(cat_id) + '類' + str(url_num_Index + 1) + '頁，共', start_id, '筆')
            print('目前打印完' + str(cat_id) + '類' + str(url_num_Index + 1) + '頁，共', start_id, '筆')
            print('目前為', str(cat_id), '類 的資料-----------------------------------StartId:', str(start_id))
            print('目前為', str(cat_id), '類 的資料-----------------------------------StartId:', str(start_id))
            print('目前為', str(cat_id), '類 的資料-----------------------------------StartId:', str(start_id))
        cat_id += 1

    # 取網頁網址
    # url = 'https://www.amazon.eg/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826028031&dc&fs=true&language=en&ds=v1%3AzsKtcEFYJVEZzlN1S09FGt9H5DUsVKszXdEGtUxJO%2F0&qid=1684666347&rnid=18017989031&ref=sr_nr_n_7'
    # pages = 20
    # print()
    # print()
    # print()
    # print('Shaving & Hair Removal')
    # await get_pagesUrl(url, pages)
    # print()
    # print()
    # print()
    # print('Skin Care')
    # url = 'https://www.amazon.eg/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826030031&dc&fs=true&language=en&ds=v1%3AgWjJUyc4a4G1ypxlBv4d6OYmqE2fusk9cE6tsKOLD%2BM&qid=1684666347&rnid=18017989031&ref=sr_nr_n_8'
    # await get_pagesUrl(url, pages)
    # print()
    # print()
    # print()
    # print('Tools & Accessories')
    # url = 'https://www.amazon.eg/s?i=beauty&bbn=18017989031&rh=n%3A18017988031%2Cn%3A21826025031&dc&fs=true&language=en&ds=v1%3ATzFw7iq6LUp01FxrKGBQP9famltCKQMNQvonvsPeDHI&qid=1684666347&rnid=18017989031&ref=sr_nr_n_9'
    # await get_pagesUrl(url, pages)


    ## 取分類表
    # 取分類網址
    # url = 'https://www.amazon.eg/s?i=beauty&bbn=18017988031&rh=n%3A18017988031&dc&fs=true&language=en&ds=v1%3AHXvG6zIMxBeuYcyG07IJ%2B5rMLcG%2FtcOobh7FlPFQbj4&qid=1684665828&ref=sr_ex_n_1'
    # cat_id = 23
    # parent_id = 23
    # sort = 23
    # await get_categories(url, cat_id, parent_id, sort)

    print('完成')



asyncio.run(main())
