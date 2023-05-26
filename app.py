import requests,json
import streamlit as st
# from config import RAKUTEN_CLIENT_ME,YAHOO_CLIENT_ME
from time import sleep
import pandas as pd

#楽天市場
MAX_PAGE = 1
RAKUTEN_CLIENT_ME = {
    'APPLICATION_ID':st.secrets["APPLICATION_ID"],
    'APPLICATION_SECRET':st.secrets["APPLICATION_SECRET"],
    'AFF_ID':st.secrets["AFF_ID"],
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
    'appid':st.secrets["APP_ID"],
}

REQ_URL = RAKUTEN_CLIENT_ME['REQ_URL']
WANT_ITEMS = RAKUTEN_CLIENT_ME['WANT_ITEMS']

#yahoo!設定
appid = YAHOO_CLIENT_ME['appid']

req_params = {
    'applicationId':RAKUTEN_CLIENT_ME['APPLICATION_ID'],
    'format':'json',
    'formatVersion':'2',
    'keyword':'',
    'sort':'+itemPrice',
    'page':0,
    'minPrice':100
}

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
                # st.dataframe(pd.DataFrame(res['Items']))
                
                for i, x in enumerate(df.iterrows()):
                    with st.expander("検索結果{}".format(i+1), expanded=True):
                        item_name = x[1]['itemName']
                        price = x[1]['itemPrice']
                        image = x[1]['mediumImageUrls']
                        url = x[1]['itemUrl']
                        caption = x[1]['itemCaption']
                        
                    with st.expander("検索結果{}".format(i+1), expanded=True):
                        cols = st.columns([1]*len(image))
                        st.write("<h3>{}</h3>".format(item_name),unsafe_allow_html=True)
                        for i in range(len(image)):
                            with cols[i]:
                                st.image(image[i])
                        
                        st.write("<h5>価格：{}円</h5>".format(price),unsafe_allow_html=True)
                        # st.write("<h5>レビュー：{}({}件)</h5>".format(review['rate'], review['count']),unsafe_allow_html=True)
                        # st.write("レビューURL：{}".format(review['url']))
                        st.write("商品説明：")
                        st.write(caption)
                        st.write("商品URL", url)

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
            

def creat_yahoo_data(arg_keywords, Lowest_price=0, Highest_price=1000000, HITS_PER_PAGE=1):
    
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
                st.write("<h3 href={}>{}</h3>".format(res_dict['hits'][i]['url'], item_name),unsafe_allow_html=True)
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
    def input_change():
        if len(st.session_state.keywords) != 0:
            st.session_state.buttonDisabled = False
        elif len(st.session_state.keywords) == 0: 
            st.session_state.buttonDisabled = True
    st.set_page_config(layout="wide")
            
    #サイドバー部分記述
    st.sidebar.write('<h3>検索対象</h3>', unsafe_allow_html=True)
    option_rakuten = st.sidebar.checkbox('楽天市場', value=True)
    option_yahoo = st.sidebar.checkbox('Yahoo!ショッピング', value=True)
    st.sidebar.write('')
    st.sidebar.write('<h3>検索件数(クリックして直接入力)</h3>', unsafe_allow_html=True)
    HITS_PER_PAGE = st.sidebar.number_input('', 1, 100, 3, label_visibility='collapsed')
    st.sidebar.write('')
    st.sidebar.write('<h3>価格範囲の指定</h3>', unsafe_allow_html=True)
    min_price, max_price = st.sidebar.select_slider(
        '',
        options=[ _ for _ in range(0,10500,500)],
        value=(0, 2000),
        label_visibility='collapsed',
    )
    req_params['minPrice'] = min_price
    req_params['hits'] = HITS_PER_PAGE
    
    #メイン画面
    st.title('ECサイト情報比較アプリ')
    st.write('<h6>検索アイテムのキーワードを入力↓</h6>', unsafe_allow_html=True)
    
    st.session_state.buttonDisabled = True
    st.session_state.keywords = ''
    col1, col2 = st.columns([6,1])
    with col1:
        st.session_state.keywords = st.text_input('', label_visibility='collapsed', on_change=input_change)

    if len(st.session_state.keywords) != 0:
        st.session_state['buttonDisabled'] = False
    else:
        st.session_state['buttonDisabled'] = True

    with col2:
        st.session_state.button_clicked = st.button('検索', disabled=st.session_state['buttonDisabled'])
        
    if st.session_state.button_clicked:
        if len(st.session_state.keywords) != 0:
            col_rakuten, col_yahoo = st.columns([1,1])
            tab1, tab2 = st.tabs(["楽天市場", "yahoo!ショッピング"])
            with tab1:
                # st.subheader('楽天市場')
                if option_rakuten:
                    create_rakuten_data([st.session_state.keywords])
            with tab2:
                # st.subheader('yahoo!ショッピング')
                if option_yahoo:
                    creat_yahoo_data(st.session_state.keywords, min_price, max_price, HITS_PER_PAGE)


if __name__ == "__main__":
    main()
