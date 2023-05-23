import requests,json
import streamlit as st
#from config import RAKUTEN_CLIENT_ME,YAHOO_CLIENT_ME
from time import sleep
import pandas as pd

RAKUTEN_CLIENT_ME = {
    'APPLICATION_ID':APPLICATION_ID,
    'APPLICATION_SECRET':APPLICATION_SECRET,
    'AFF_ID':AFF_ID,
    'REQ_URL':'https://app.rakuten.co.jp/services/api/IchibaItem/Search/20170706',
    'WANT_ITEMS':['itemName',
                  'genreId',
                  'itemPrice',
                  'catchcopy',
                  'itemCaption',
                  'reviewAverage',
                  # 'reviewCount',
                  # 'shopCode',
                  'shopName',
                  'itemUrl',
                  'smallImageUrls',
                  'mediumImageUrls',
                 ]
    
}

YAHOO_CLIENT_ME = {
    'YahooItemSearchURL':"https://shopping.yahooapis.jp/ShoppingWebService/V3/itemSearch",
    'appid':appid,
}
#楽天市場
MAX_PAGE = 1
HITS_PER_PAGE = 3
REQ_URL = RAKUTEN_CLIENT_ME['REQ_URL']
WANT_ITEMS = RAKUTEN_CLIENT_ME['WANT_ITEMS']

#yahoo!設定
appid = YAHOO_CLIENT_ME['appid']

req_params = {
    'applicationId':RAKUTEN_CLIENT_ME['APPLICATION_ID'],
    'format':'json',
    'formatVersion':'2',
    'keyword':'',
    'hits':HITS_PER_PAGE,
    'sort':'+itemPrice',
    'page':0,
    'minPrice':100
}
#'postageFlag':1 #送料フラグ 0->全て,1->送料込み


def create_rakuten_data(arg_keywords):
    #キーワードループ
    for keyword in arg_keywords:
        #初期設定
        cnt = 1
        keyword = keyword.replace('\u3000',' ')
        req_params['keyword'] = keyword
        df = pd.DataFrame(columns=WANT_ITEMS)

        #ページループ
        while True:
            req_params['page'] = cnt
            res = requests.get(REQ_URL,req_params)
            res_code = res.status_code
            res = json.loads(res.text)
            if res_code != 200:
                print(f"ErrorCode --> {res_code}\nError --> {res['error']}\nPage --> {cnt}")
            else:
                #返ってきた商品数の数が0の場合はループ終了
                if res['hits'] == 0:
                    break
                
                tmp_df = pd.DataFrame(res['Items'])[WANT_ITEMS]
                df = pd.concat([df,tmp_df],ignore_index=True)

                for x in df.iterrows():
                    item_name = x[1]['itemName']
                    # description = res_dict['hits'][i]['description']
                    # description = description.replace('<br>', '\n')
                    # shipping = res_dict['hits'][i]['shipping']['name']
                    # review = res_dict['hits'][i]['review']
                    # image = res_dict['hits'][i]['image']['small']
                    st.write("商品名：")
                    st.write(item_name)
                    # st.image(image)
                    # st.write("価格：{}円  {}".format(res_dict['hits'][i]['price'], shipping))
                    # st.write("レビュー：{}({}件) URL：{}".format(review['rate'], review['count'], review['url']))
                    # st.write("説明：", description)
                    # st.write("商品URL", res_dict['hits'][i]['url'])
            
            if cnt == MAX_PAGE:
                break
            
            cnt += 1
            #リクエスト制限回避
            sleep(1)
            
def creat_yahoo_data(arg_keywords, Lowest_price=0, Highest_price=1000000):
    
    keywords = arg_keywords.replace('\u3000',' ')

    url = 'https://shopping.yahooapis.jp/ShoppingWebService/V3/itemSearch?appid={}&price_from={}&price_to={}&query={}&results={}'.format(appid, Lowest_price, Highest_price, keywords, HITS_PER_PAGE)
    call = requests.get(url)
    res_dict = json.loads(call.content)
    count = len(res_dict['hits'])

    for i in range(count):
        #shipping,sellerのnameとreview,image,review
        item_name = res_dict['hits'][i]['name']
        description = res_dict['hits'][i]['description']
        description = description.replace('<br>', '\n')
        shipping = res_dict['hits'][i]['shipping']['name']
        review = res_dict['hits'][i]['review']
        image = res_dict['hits'][i]['image']['small']
        with st.expander("検索結果{}".format(i+1), expanded=True):
            col1, col2 = st.columns([6,1])
            with col1:
                st.subheader(item_name)
            with col2:
                st.image(image)
            # st.subheader(item_name)
            # st.image(image)
            st.write("<h5>価格：{}円  {}</h5>".format(res_dict['hits'][i]['price'], shipping),unsafe_allow_html=True)
            st.write("<h5>レビュー：{}({}件)</h5>".format(review['rate'], review['count']),unsafe_allow_html=True)
            st.write("URL：{}".format(review['url']))
            st.write("商品説明：")
            st.write(description)
            st.write("商品URL", res_dict['hits'][i]['url'])

def main():
    
    st.sidebar.write('検索対象')
    option_rakuten = st.sidebar.checkbox('楽天市場', value=True)
    option_yahoo = st.sidebar.checkbox('Yahoo!ショッピング', value=True)

    min_price, max_price = st.sidebar.select_slider(
        '価格範囲の設定',
        options=[ _ for _ in range(0,10500,500)],
        value=(0, 2000),
    )
    req_params['minPrice'] = min_price
    
    st.title('ECサイト情報比較アプリ')
    keywords = ''
    keywords = st.text_input('検索アイテムのキーワードを入力','')
    

    
    col1, col2 = st.columns(2, gap="large")
    with col1:
        st.header("A cat")
    with col2:
        st.header("A cat")
    
    if len(keywords) != 0:
        if option_rakuten:
            create_rakuten_data([keywords])
        if option_yahoo:
            creat_yahoo_data(keywords, min_price, max_price)

if __name__ == "__main__":
    main()
