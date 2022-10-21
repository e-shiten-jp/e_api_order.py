# -*- coding: utf-8 -*-
# Copyright (c) 2021 Tachibana Securities Co., Ltd. All rights reserved.

# 2021.07.07,   yo.
# 2022.10.20 reviced,   yo.
# Python 3.6.8 / centos7.4
# API v4r3で動作確認
# 立花証券ｅ支店ＡＰＩ利用のサンプルコード
# ログインして属性取得、可能額取得、現物買い注文、その注文の取消、注文一覧取得、ログアウトします。

import urllib3
import datetime
import json
import time


# request項目を保存するクラス。配列として使う。
# 'p_no'、'p_sd_date'は格納せず、func_make_url_requestで生成する。
class class_req :
    def __init__(self) :
        self.str_key = ''
        self.str_value = ''
        
    def add_data(self, work_key, work_value) :
        self.str_key = func_check_json_dquat(work_key)
        self.str_value = func_check_json_dquat(work_value)


# 口座属性クラス
class class_def_cust_property:
    def __init__(self):
        self.sUrlRequest = ''       # request用仮想URL
        self.sUrlMaster = ''        # master用仮想URL
        self.sUrlPrice = ''         # price用仮想URL
        self.sUrlEvent = ''         # event用仮想URL
        self.sZyoutoekiKazeiC = ''  # 8.譲渡益課税区分    1：特定  3：一般  5：NISA     ログインの返信データで設定済み。 
        self.sSecondPassword = ''   # 22.第二パスワード  APIでは第２暗証番号を省略できない。 関連資料:「立花証券・e支店・API、インターフェース概要」の「3-2.ログイン、ログアウト」参照
        self.sJsonOfmt = ''         # 返り値の表示形式指定
        


# システム時刻を"p_sd_date"の書式の文字列で返す。
# 書式：YYYY.MM.DD-hh:mm:ss.sss
def func_p_sd_date(int_systime):
    str_psddate = ''
    str_psddate = str_psddate + str(int_systime.year) 
    str_psddate = str_psddate + '.' + ('00' + str(int_systime.month))[-2:]
    str_psddate = str_psddate + '.' + ('00' + str(int_systime.day))[-2:]
    str_psddate = str_psddate + '-' + ('00' + str(int_systime.hour))[-2:]
    str_psddate = str_psddate + ':' + ('00' + str(int_systime.minute))[-2:]
    str_psddate = str_psddate + ':' + ('00' + str(int_systime.second))[-2:]
    str_psddate = str_psddate + '.' + (('000000' + str(int_systime.microsecond))[-6:])[:3]
    return str_psddate


# JSONの値の前後にダブルクオーテーションが無い場合付ける。
def func_check_json_dquat(str_value) :
    if len(str_value) == 0 :
        str_value = '""'
        
    if not str_value[:1] == '"' :
        str_value = '"' + str_value
        
    if not str_value[-1:] == '"' :
        str_value = str_value + '"'
        
    return str_value
    
    
# 受けたテキストの１文字目と最終文字の「"」を削除
# 引数：string
# 返り値：string
def func_strip_dquot(text):
    if len(text) > 0:
        if text[0:1] == '"' :
            text = text[1:]
            
    if len(text) > 0:
        if text[-1] == '\n':
            text = text[0:-1]
        
    if len(text) > 0:
        if text[-1:] == '"':
            text = text[0:-1]
        
    return text
    


# URLエンコード文字の変換
#
# URLに「#」「+」「/」「:」「=」などの記号を利用した場合エラーとなる場合がある。
# APIへの入力文字列（特にパスワードで記号を利用している場合）で注意が必要。
#   '#' →   '%23'
#   '+' →   '%2B'
#   '/' →   '%2F'
#   ':' →   '%3A'
#   '=' →   '%3D'
def func_replace_urlecnode( str_input ):
    str_encode = ''
    str_replace = ''
    
    for i in range(len(str_input)):
        str_char = str_input[i:i+1]

        if str_char == ' ' :
            str_replace = '%20'       #「 」 → 「%20」 半角空白
        elif str_char == '!' :
            str_replace = '%21'       #「!」 → 「%21」
        elif str_char == '"' :
            str_replace = '%22'       #「"」 → 「%22」
        elif str_char == '#' :
            str_replace = '%23'       #「#」 → 「%23」
        elif str_char == '$' :
            str_replace = '%24'       #「$」 → 「%24」
        elif str_char == '%' :
            str_replace = '%25'       #「%」 → 「%25」
        elif str_char == '&' :
            str_replace = '%26'       #「&」 → 「%26」
        elif str_char == "'" :
            str_replace = '%27'       #「'」 → 「%27」
        elif str_char == '(' :
            str_replace = '%28'       #「(」 → 「%28」
        elif str_char == ')' :
            str_replace = '%29'       #「)」 → 「%29」
        elif str_char == '*' :
            str_replace = '%2A'       #「*」 → 「%2A」
        elif str_char == '+' :
            str_replace = '%2B'       #「+」 → 「%2B」
        elif str_char == ',' :
            str_replace = '%2C'       #「,」 → 「%2C」
        elif str_char == '/' :
            str_replace = '%2F'       #「/」 → 「%2F」
        elif str_char == ':' :
            str_replace = '%3A'       #「:」 → 「%3A」
        elif str_char == ';' :
            str_replace = '%3B'       #「;」 → 「%3B」
        elif str_char == '<' :
            str_replace = '%3C'       #「<」 → 「%3C」
        elif str_char == '=' :
            str_replace = '%3D'       #「=」 → 「%3D」
        elif str_char == '>' :
            str_replace = '%3E'       #「>」 → 「%3E」
        elif str_char == '?' :
            str_replace = '%3F'       #「?」 → 「%3F」
        elif str_char == '@' :
            str_replace = '%40'       #「@」 → 「%40」
        elif str_char == '[' :
            str_replace = '%5B'       #「[」 → 「%5B」
        elif str_char == ']' :
            str_replace = '%5D'       #「]」 → 「%5D」
        elif str_char == '^' :
            str_replace = '%5E'       #「^」 → 「%5E」
        elif str_char == '`' :
            str_replace = '%60'       #「`」 → 「%60」
        elif str_char == '{' :
            str_replace = '%7B'       #「{」 → 「%7B」
        elif str_char == '|' :
            str_replace = '%7C'       #「|」 → 「%7C」
        elif str_char == '}' :
            str_replace = '%7D'       #「}」 → 「%7D」
        elif str_char == '~' :
            str_replace = '%7E'       #「~」 → 「%7E」
        else :
            str_replace = str_char

        str_encode = str_encode + str_replace
        
    return str_encode



# 機能： API問合せ文字列を作成し返す。
# 戻り値： url文字列
# 第１引数： ログインは、Trueをセット。それ以外はFalseをセット。
# 第２引数： ログインは、APIのurlをセット。それ以外はログインで返された仮想url（'sUrlRequest'等）の値をセット。
# 第３引数： 要求項目のデータセット。クラスの配列として受取る。
def func_make_url_request(auth_flg, \
                          url_target, \
                          work_class_req) :
    
    str_url = url_target
    if auth_flg == True :
        str_url = str_url + 'auth/'
    
    str_url = str_url + '?{\n\t'
    
    for i in range(len(work_class_req)) :
        if len(work_class_req[i].str_key) > 0:
            str_url = str_url + work_class_req[i].str_key + ':' + work_class_req[i].str_value + ',\n\t'
        
    str_url = str_url[:-3] + '\n}'
    return str_url



# 機能： API問合せ。通常のrequest,price用。
# 第１引数： URL文字列。
# 備考: APIに接続し、requestの文字列を送信し、応答データを辞書型で返す。
#       master取得は専用の func_api_req_muster を利用する。
def func_api_req(str_url): 
    print('送信文字列＝')
    print(str_url)  # 送信する文字列

    # APIに接続
    http = urllib3.PoolManager()
    req = http.request('GET', str_url)
    print("req.status= ", req.status )

    # 取得したデータがbytes型なので、json.loadsを利用できるようにstr型に変換する。日本語はshift-jis。
    bytes_reqdata = req.data
    str_shiftjis = bytes_reqdata.decode("shift-jis", errors="ignore")

    print('返信文字列＝')
    print(str_shiftjis)

    # JSON形式の文字列を辞書型で取り出す
    json_req = json.loads(str_shiftjis)

    return json_req



# ログイン関数
# 引数1: p_noカウンター
# 引数2: アクセスするurl（'auth/'以下は付けない）
# 引数3: ユーザーID
# 引数4: パスワード
# 引数5: 口座属性クラス
# 返値：辞書型データ（APIからのjson形式返信データをshift-jisのstring型に変換し、更に辞書型に変換）
def func_login(int_p_no, url_base, my_userid, my_passwd, class_cust_property):
    # 送信項目の解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇）、REQUEST I/F、機能毎引数項目仕様」
    # p2/43 No.1 引数名:CLMAuthLoginRequest を参照してください。
    
    req_item = [class_req()]
    str_p_sd_date = func_p_sd_date(datetime.datetime.now())     # システム時刻を所定の書式で取得

    str_key = '"p_no"'
    str_value = func_check_json_dquat(str(int_p_no))
    #req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    str_key = '"p_sd_date"'
    str_value = str_p_sd_date
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    str_key = '"sCLMID"'
    str_value = 'CLMAuthLoginRequest'
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    str_key = '"sUserId"'
    str_value = my_userid
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)
    
    str_key = '"sPassword"'
    str_value = my_passwd
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)
    
    # 返り値の表示形式指定
    str_key = '"sJsonOfmt"'
    str_value = class_cust_property.sJsonOfmt    # "5"は "1"（ビット目ＯＮ）と”4”（ビット目ＯＮ）の指定となり「ブラウザで見や易い形式」且つ「引数項目名称」で応答を返す値指定
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    # ログインとログイン後の電文が違うため、第１引数で指示。
    # ログインはTrue。それ以外はFalse。
    # このプログラムでの仕様。APIの仕様ではない。
    # URL文字列の作成
    str_url = func_make_url_request(True, \
                                     url_base, \
                                     req_item)
    # API問合せ
    json_return = func_api_req(str_url)
    # 戻り値の解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇）、REQUEST I/F、機能毎引数項目仕様」
    # p2/43 No.2 引数名:CLMAuthLoginAck を参照してください。

    int_p_errno = int(json_return.get('p_errno'))    # p_erronは、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇ｒ〇）、REQUEST I/F、利用方法、データ仕様」を参照ください。
    int_sResultCode = int(json_return.get('sResultCode'))
    # sResultCodeは、マニュアル
    # 「立花証券・ｅ支店・ＡＰＩ（ｖ〇ｒ〇）、REQUEST I/F、注文入力機能引数項目仕様」
    # (api_request_if_order_vOrO.pdf)
    # の p13/42 「6.メッセージ一覧」を参照ください。

    if int_p_errno ==  0 and int_sResultCode == 0:    # ログインエラーでない場合
        # ---------------------------------------------
        # ログインでの注意点
        # 契約締結前書面が未読の場合、
        # 「int_p_errno = 0 And my_sResultCode = 0」で、
        # sUrlRequest=""、sUrlEvent="" が返されログインできない。
        # ---------------------------------------------
        if len(json_return.get('sUrlRequest')) > 0 :
            # 口座属性クラスに取得した値をセット
            class_cust_property.sZyoutoekiKazeiC = json_return.get('sZyoutoekiKazeiC')
            class_cust_property.sUrlRequest = json_return.get('sUrlRequest')        # request用仮想URL
            class_cust_property.sUrlMaster = json_return.get('sUrlMaster')          # master用仮想URL
            class_cust_property.sUrlPrice = json_return.get('sUrlPrice')            # price用仮想URL
            class_cust_property.sUrlEvent = json_return.get('sUrlEvent')            # event用仮想URL
            bool_login = True
        else :
            print('契約締結前書面が未読です。')
            print('ブラウザーで標準Webにログインして確認してください。')
    else :  # ログインに問題があった場合
        print('p_errno:', json_return.get('p_errno'))
        print('p_err:', json_return.get('p_err'))
        print('sResultCode:', json_return.get('sResultCode'))
        print('sResultText:', json_return.get('sResultText'))
        print()
        bool_login = False
        
    return bool_login


# ログアウト
# 引数1: p_noカウンター
# 引数2: class_cust_property（request通番）, 口座属性クラス
# 返値：辞書型データ（APIからのjson形式返信データをshift-jisのstring型に変換し、更に辞書型に変換）
def func_logout(int_p_no, class_cust_property):
    # 送信項目の解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇）、REQUEST I/F、機能毎引数項目仕様」
    # p3/43 No.3 引数名:CLMAuthLogoutRequest を参照してください。
    
    req_item = [class_req()]
    str_p_sd_date = func_p_sd_date(datetime.datetime.now())     # システム時刻を所定の書式で取得

    str_key = '"p_no"'
    str_value = func_check_json_dquat(str(int_p_no))
    #req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    str_key = '"p_sd_date"'
    str_value = str_p_sd_date
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    str_key = '"sCLMID"'
    str_value = 'CLMAuthLogoutRequest'  # logoutを指示。
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)
    
    # 返り値の表示形式指定
    str_key = '"sJsonOfmt"'
    str_value = class_cust_property.sJsonOfmt    # "5"は "1"（ビット目ＯＮ）と”4”（ビット目ＯＮ）の指定となり「ブラウザで見や易い形式」且つ「引数項目名称」で応答を返す値指定
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)
    
    # ログインとログイン後の電文が違うため、第１引数で指示。
    # ログインはTrue。それ以外はFalse。
    # このプログラムでの仕様。APIの仕様ではない。
    # URL文字列の作成
    str_url = func_make_url_request(False, \
                                     class_cust_property.sUrlRequest, \
                                     req_item)
    # API問合せ
    json_return = func_api_req(str_url)
    # 戻り値の解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇）、REQUEST I/F、機能毎引数項目仕様」
    # p3/43 No.4 引数名:CLMAuthLogoutAck を参照してください。

    int_sResultCode = int(json_return.get('sResultCode'))    # p_erronは、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇ｒ〇）、REQUEST I/F、利用方法、データ仕様」を参照ください。
    if int_sResultCode ==  0 :    # ログアウトエラーでない場合
        bool_logout = True
    else :  # ログアウトに問題があった場合
        bool_logout = False

    return bool_logout





# 可能額取得
# 引数1: p_noカウンター 
# 引数2: 口座属性クラス
def func_kanougaku(int_p_no, class_cust_property):
    # 送信項目の解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇）、REQUEST I/F、機能毎引数項目仕様」
    # p10/43 No.10 引数名:CLMZanKaiKanougaku を参照してください。

    req_item = [class_req()]
    str_p_sd_date = func_p_sd_date(datetime.datetime.now())     # システム時刻を所定の書式で取得

    str_key = '"p_no"'
    str_value = func_check_json_dquat(str(int_p_no))
    #req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    str_key = '"p_sd_date"'
    str_value = str_p_sd_date
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)
    
    str_key = '"sCLMID"'
    str_value = 'CLMZanKaiKanougaku'  # 買余力を指示。
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    # 返り値の表示形式指定
    str_key = '"sJsonOfmt"'
    str_value = class_cust_property.sJsonOfmt    # "5"は "1"（ビット目ＯＮ）と”4”（ビット目ＯＮ）の指定となり「ブラウザで見や易い形式」且つ「引数項目名称」で応答を返す値指定
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    # URL文字列の作成
    str_url = func_make_url_request(False, \
                                     class_cust_property.sUrlRequest, \
                                     req_item)
    # API問合せ
    json_return = func_api_req(str_url)
    # 戻り値の解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇）、REQUEST I/F、機能毎引数項目仕様」
    # p10/43 No.10 引数名:CLMZanKaiKanougaku を参照してください。

    return json_return




# 現物買い注文関数
# 引数：銘柄コード、市場（現在、東証'00'のみ）、執行条件、価格、株数、口座属性クラス
# 返値：辞書型データ（APIからのjson形式返信データをshift-jisのstring型に変換し、更に辞書型に変換）
def func_order_buy_genbutsu(int_p_no, str_sIssueCode, str_sSizyouC, str_sCondition, str_sOrderPrice, str_sOrderSuryou, class_cust_property):
    # 送信項目の解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇）、REQUEST I/F、機能毎引数項目仕様」
    # p4/43 No.5 引数名:CLMKabuNewOrder を参照してください。


    req_item = [class_req()]
##    class_cust_property.int_p_no += 1
    str_p_sd_date = func_p_sd_date(datetime.datetime.now())     # システム時刻を所定の書式で取得
        
    str_sGenkinShinyouKubun = '0'    # 16.現金信用区分  0:現物、2:新規(制度信用6ヶ月)、4:返済(制度信用6ヶ月)、6:新規(一般信用6ヶ月)、8:返済(一般信用6ヶ月)。
    str_sBaibaiKubun = '3'   # 12.売買区分  1:売、3:買、5:現渡、7:現引。

    # 固定パラメーターセット
    #str_sZyoutoekiKazeiC            # 8.譲渡益課税区分    1：特定  3：一般  5：NISA     ログインの返信データで設定済み。 
    str_sOrderExpireDay = '0'        # 17.注文期日  0:当日、上記以外は、注文期日日(YYYYMMDD)[10営業日迄]。
    str_sGyakusasiOrderType = '0'    # 18.逆指値注文種別  0:通常、1:逆指値、2:通常+逆指値
    str_sGyakusasiZyouken = '0'      # 19.逆指値条件  0:指定なし、条件値段(トリガー価格)
    str_sGyakusasiPrice = '*'        # 20.逆指値値段  *:指定なし、0:成行、*,0以外は逆指値値段。
    str_sTatebiType = '*'            # 21.建日種類  *:指定なし(現物または新規) 、1:個別指定、2:建日順、3:単価益順、4:単価損順。
    str_sTategyokuZyoutoekiKazeiC =  '*'    # 9.建玉譲渡益課税区分  信用建玉における譲渡益課税区分(現引、現渡で使用)。  *:現引、現渡以外の取引、1:特定、3:一般、5:NISA
    #str_sSecondPassword             # 22.第二パスワード    APIでは第２暗証番号を省略できない。 関連資料:「立花証券・e支店・API、インターフェース概要」の「3-2.ログイン、ログアウト」参照     ログインの返信データで設定済み。
    

    str_key = '"p_no"'
    str_value = func_check_json_dquat(str(int_p_no))
    #req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    str_key = '"p_sd_date"'
    str_value = str_p_sd_date
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)
    
    # API request区分
    str_key = '"sCLMID"'
    str_value = 'CLMKabuNewOrder'  # 新規注文を指示。
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    # 現物信用区分
    str_key = '"sGenkinShinyouKubun"'    # 現金信用区分
    str_value = str_sGenkinShinyouKubun
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)


    # 注文パラメーターセット
    str_key = '"sIssueCode"'    # 銘柄コード
    str_value = str_sIssueCode
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    str_key = '"sSizyouC"'    # 市場C
    str_value = str_sSizyouC
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    str_key = '"sBaibaiKubun"'    # 売買区分
    str_value = str_sBaibaiKubun
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)
    
    str_key = '"sCondition"'    # 執行条件
    str_value = str_sCondition
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    str_key = '"sOrderPrice"'    # 注文値段
    str_value = str_sOrderPrice
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    str_key = '"sOrderSuryou"'    # 注文数量
    str_value = str_sOrderSuryou
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)


    # 固定パラメーターセット
    str_key = '"sZyoutoekiKazeiC"'  # 税口座区分
    str_value = class_cust_property.sZyoutoekiKazeiC    # 引数の口座属性クラスより取得
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    str_key = '"sOrderExpireDay"'    # 注文期日
    str_value = str_sOrderExpireDay
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    str_key = '"sGyakusasiOrderType"'    # 逆指値注文種別
    str_value = str_sGyakusasiOrderType
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    str_key = '"sGyakusasiZyouken"'    # 逆指値条件
    str_value = str_sGyakusasiZyouken
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    str_key = '"sGyakusasiPrice"'    # 逆指値値段
    str_value = str_sGyakusasiPrice
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    str_key = '"sTatebiType"'    # 建日種類
    str_value = str_sTatebiType
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    str_key = '"sTategyokuZyoutoekiKazeiC"'     # 9.建玉譲渡益課税区分
    str_value = str_sTategyokuZyoutoekiKazeiC
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    str_key = '"sSecondPassword"'    # 第二パスワード   APIでは第２暗証番号を省略できない。
    print('class_cust_property.sSecondPassword:', class_cust_property.sSecondPassword)
    str_value = class_cust_property.sSecondPassword     # 引数の口座属性クラスより取得
    req_item.append(class_req())
    
    req_item[-1].add_data(str_key, str_value)

    # 返り値の表示形式指定
    str_key = '"sJsonOfmt"'
    str_value = class_cust_property.sJsonOfmt    # "5"は "1"（ビット目ＯＮ）と”4”（ビット目ＯＮ）の指定となり「ブラウザで見や易い形式」且つ「引数項目名称」で応答を返す値指定
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    # URL文字列の作成
    str_url = func_make_url_request(False, \
                                     class_cust_property.sUrlRequest, \
                                     req_item)

    json_return = func_api_req(str_url)
    # 戻り値の解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇）、REQUEST I/F、機能毎引数項目仕様」(api_request_if_clumn_v4.pdf)
    # p4-5/43 No.5 引数名:CLMKabuNewOrder 項目1-28 を参照してください。
    
    return json_return      # 注文のjson応答文を返す



# 注文取消
# 引数：注文番号、営業日、口座属性クラス
# 返値：辞書型データ（APIからのjson形式返信データをshift-jisのstring型に変換し、更に辞書型に変換）
def func_cancel_order(int_p_no, str_sOrderNumber, str_sEigyouDay, class_cust_property):
    # 送信項目の解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇）、REQUEST I/F、機能毎引数項目仕様」(api_request_if_clumn_v4.pdf)
    # p6/43 No.7 引数名:CLMKabuCancelOrder を参照してください。
    # 注文取り消しは、現物、信用等の区別はない。

    req_item = [class_req()]
    str_p_sd_date = func_p_sd_date(datetime.datetime.now())     # システム時刻を所定の書式で取得
        

    str_key = '"p_no"'
    str_value = func_check_json_dquat(str(int_p_no))
    #req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    str_key = '"p_sd_date"'
    str_value = str_p_sd_date
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)
    
    # API request区分
    str_key = '"sCLMID"'
    str_value = '"CLMKabuCancelOrder"'  # 注文取消を指示。
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)
    
    # 注文番号
    str_key = '"sOrderNumber"'    # 注文番号
    str_value = str_sOrderNumber
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)
    
    str_key = '"sEigyouDay"'    # 営業日
    str_value = str_sEigyouDay
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    str_key = '"sSecondPassword"'    # 第二パスワード  APIでは第２暗証番号を省略しない。
    str_value = class_cust_property.sSecondPassword
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    # 返り値の表示形式指定
    str_key = '"sJsonOfmt"'
    str_value = class_cust_property.sJsonOfmt    # "5"は "1"（ビット目ＯＮ）と”4”（ビット目ＯＮ）の指定となり「ブラウザで見や易い形式」且つ「引数項目名称」で応答を返す値指定
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)


    # URL文字列の作成
    str_url = func_make_url_request(False, \
                                     class_cust_property.sUrlRequest, \
                                     req_item)

    for i in range(30):     # 元注文が処理中の場合の待機処理。max30s。
        json_return = func_api_req(str_url)
        # 戻り値の解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇）、REQUEST I/F、機能毎引数項目仕様」
        # p6/43 No.7 引数名:CLMKabuCancelOrder を参照してください。
        
        if json_return.get('sResultCode') == '13290':   # 元注文が処理中の場合
            time.sleep(1)   # 引数の秒数のウエイト
            print('wait : ', (i+1))

        else:
            break

    return json_return




# 注文一覧の取得
# 引数：銘柄コード（指定無しは全一覧を取得）、口座属性クラス
# 返値：辞書型データ（APIからのjson形式返信データをshift-jisのstring型に変換し、更に辞書型に変換）
def func_get_order_list(int_p_no, str_code, class_cust_property):
    # 送信項目の解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇）、REQUEST I/F、機能毎引数項目仕様」
    # p12/43 No.13 引数名:CLMOrderList を参照してください。
        
    req_item = [class_req()]
    str_p_sd_date = func_p_sd_date(datetime.datetime.now())     # システム時刻を所定の書式で取得
    
    str_key = '"p_no"'
    str_value = func_check_json_dquat(str(int_p_no))
    #req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    str_key = '"p_sd_date"'
    str_value = str_p_sd_date
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)
    
    str_key = '"sCLMID"'
    str_value = 'CLMOrderList'
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)


    str_key = '"sIssueCode"'
    str_value = str_code
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    str_key = '"sSikkouDay"'
    str_value = datetime.datetime.now().strftime('%Y%m%d')
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)
    
    # 返り値の表示形式指定
    str_key = '"sJsonOfmt"'
    str_value = class_cust_property.sJsonOfmt    # "5"は "1"（ビット目ＯＮ）と”4”（ビット目ＯＮ）の指定となり「ブラウザで見や易い形式」且つ「引数項目名称」で応答を返す値指定
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    # URL文字列の作成
    str_url = func_make_url_request(False, \
                                     class_cust_property.sUrlRequest, \
                                     req_item)

    json_return = func_api_req(str_url)
    # 戻り値の解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇）、REQUEST I/F、機能毎引数項目仕様」
    # p12-14/43 No.13 引数名:CLMOrderList 1-42 を参照してください。
    # 複数行データがあるとjsonデータがネストする

    return json_return







    
    
# ======================================================================================================
# ==== プログラム始点 =================================================================================
# ======================================================================================================

# --- 利用時に変数を設定してください -------------------------------------------------------

# 接続先 設定 --------------
# デモ環境（新バージョンになった場合、適宜変更）
# デモ環境は今のところメンテナンス待ちのため、注文、取消では利用できません。
url_base = 'https://demo-kabuka.e-shiten.jp/e_api_v4r2/'
##url_base = 'https://demo-kabuka.e-shiten.jp/e_api_v4r3/'

# 本番環境（新バージョンになった場合、適宜変更）
# ＊＊！！実際に市場に注文が出るので注意！！＊＊
# url_base = 'https://kabuka.e-shiten.jp/e_api_v4r3/'

# ＩＤパスワード設定 ---------
my_userid = 'MY_USERID' # 自分のuseridに書き換える
my_passwd = 'MY_PASSWD' # 自分のpasswordに書き換える
my_2pwd = 'MY_2PASSWD'  # 自分の第２passwordに書き換える


# 現物買い注文パラメーターセット
##my_code = '1234'    # 10.銘柄コード。実際の銘柄コードを入れてください。
my_code = '1301'    # 10.銘柄コード。実際の銘柄コードを入れてください。
my_shijyou = '00'   # 11.市場。  00:東証   現在(2021/07/01)、東証のみ可能。
my_shikkou = '0'    # 13.執行条件。  0:指定なし、2:寄付、4:引け、6:不成。指し値は、0:指定なし。
my_kakaku = '000'   # 14.注文値段。  *:指定なし、0:成行、上記以外は、注文値段。小数点については、関連資料:「立花証券・e支店・API、REQUEST I/F、マスタデータ利用方法」の「2-12. 呼値」参照。
my_kabusuu = '100'  # 15.注文数量。


# --- 以上設定項目 -------------------------------------------------------------------------


class_cust_property = class_def_cust_property()     # 口座属性クラス

# ID、パスワードのURLエンコードをチェックして変換
str_userid = func_replace_urlecnode(my_userid)
str_passwd = func_replace_urlecnode(my_passwd)
class_cust_property.sSecondPassword = func_replace_urlecnode(my_2pwd)
# 返り値の表示形式指定
class_cust_property.sJsonOfmt = '5'
# "5"は "1"（1ビット目ＯＮ）と”4”（3ビット目ＯＮ）の指定となり
# ブラウザで見や易い形式」且つ「引数項目名称」で応答を返す値指定

print('-- login -----------------------------------------------------')
## 「ｅ支店・ＡＰＩ、ブラウザからの利用方法」に記載のログイン例
## 'https://demo-kabuka.e-shiten.jp/e_api_v4r1/auth/?{"p_no":"1","p_sd_date":"2020.11.07-13:46:35.000",'
## '"sCLMID":"CLMAuthLoginRequest","sPassword":"xxxxxx","sUserId":"xxxxxxxx","sJsonOfmt":"5"}'
##
# 送信項目の解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇）、REQUEST I/F、機能毎引数項目仕様」
# p2/43 No.1 引数名:CLMAuthLoginRequest を参照してください。

int_p_no = 1
# ログイン処理
bool_login = func_login(int_p_no, url_base, str_userid, str_passwd,  class_cust_property)
# 戻り値の解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇）、REQUEST I/F、機能毎引数項目仕様」
# p2/43 No.2 引数名:CLMAuthLoginAck を参照してください。


# ログインOKの場合
if bool_login :
    
    print()
    print('-- 買余力の照会 -------------------------------------------------------------')

    int_p_no = int_p_no + 1
    # 可能額取得
    json_return = func_kanougaku(int_p_no, class_cust_property)
    # 戻り値の解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇）、REQUEST I/F、機能毎引数項目仕様」
    # p10/43 No.10 引数名:CLMZanKaiKanougaku を参照してください。
    
    print('更新日時= ', json_return.get("sSummaryUpdate"))     # 株式現物買付可能額
    print('株式現物買付可能額= ', json_return.get("sSummaryGenkabuKaituke"))     # 株式現物買付可能額
    print('NISA口座買付可能額= ', json_return.get("sSummaryNisaKaitukeKanougaku"))     # NISA口座買付可能額


    print()
    print('-- 現物買付注文  -------------------------------------------------------------')
    
    # 送信項目の解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇）、REQUEST I/F、機能毎引数項目仕様」
    # p4/43 No.5 引数名:CLMZanKaiKanougaku を参照してください。

    
    # 送信項目の実例は、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ４）、REQUEST I/F、注文入力機能引数項目仕様」
    # p5/40 以降にrequest電文と応答電文を記載
    # 「現物×買×成行×特定口座」のrequest電文例
    # {
    #   "sCLMID":"CLMKabuNewOrder",
    #   "sZyoutoekiKazeiC":"1",
    #   "sIssueCode":"6658",
    #   "sSizyouC":"00",
    #   "sBaibaiKubun":"3",
    #   "sCondition":"0",
    #   "sOrderPrice":"0",
    #   "sOrderSuryou":"100",
    #   "sGenkinShinyouKubun":"0",
    #   "sOrderExpireDay":"0",
    #   "sGyakusasiOrderType":"0",
    #   "sGyakusasiZyouken":"0",
    #   "sGyakusasiPrice":"*",
    #   "sTatebiType":"*",
    #   "sTategyokuZyoutoekiKazeiC":"*",
    #   "sSecondPassword":"",
    #   "sJsonOfmt":"1"
    # }
    # この注文例を基にrequest電文を作成してみる
 

    # 当日の現物注文（逆指値等は使わない）でパラメーターを減らした簡単な関数例
    
    # 注文パラメーターセット
    str_sIssueCode = my_code         # 10.銘柄コード。実際の銘柄コードを入れてください。# パスワード設定の下の行で設定した銘柄コード
    str_sSizyouC = my_shijyou        # 11.市場  00:東証   現在(2021/07/01)、東証のみ可能。
    str_sCondition = my_shikkou      # 13.執行条件  0:指定なし、2:寄付、4:引け、6:不成。指し値は、0:指定なし。
    str_sOrderPrice = my_kakaku      # 14.注文値段  *:指定なし、0:成行、上記以外は、注文値段。小数点については、関連資料:「立花証券・e支店・API、REQUEST I/F、マスタデータ利用方法」の「2-12. 呼値」参照。
    str_sOrderSuryou = my_kabusuu    # 15.注文数量。

    int_p_no = int_p_no + 1
    # 現物買い注文    引数：銘柄コード、市場（現在、東証'00'のみ）、執行条件、価格、株数、口座属性クラス
    json_return = func_order_buy_genbutsu(int_p_no, str_sIssueCode, str_sSizyouC, str_sCondition, str_sOrderPrice, str_sOrderSuryou, class_cust_property)
    # 戻り値の解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇）、REQUEST I/F、機能毎引数項目仕様」(api_request_if_clumn_v4.pdf)
    # p4-5/43 No.5 引数名:CLMKabuNewOrder 項目1-28 を参照してください。

    str_sOrderNumber = json_return.get('sOrderNumber')     # 注文番号
    str_sEigyouDay = json_return.get('sEigyouDay')         # 営業日
    


    print()
    print('-- 注文取消  -------------------------------------------------------------')
    # 送信項目の解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇）、REQUEST I/F、機能毎引数項目仕様」(api_request_if_clumn_v4.pdf)
    # p6/43 No.7 引数名:CLMKabuCancelOrder を参照してください。
    # 注文取り消しは、現物、信用等の区別はない。

    # 上で出した注文を取り消す。
    # 注文取り消し
    # 引数：注文番号、営業日、口座属性クラス
    # 営業日、翌営業日は、マスターダウンロードで取得可能。大引けまでは「営業日」、１６時頃（日々変動あり）の翌日注文開始以降は「翌営業日」をセット。
    int_p_no = int_p_no + 1
    json_return = func_cancel_order(int_p_no, str_sOrderNumber, str_sEigyouDay, class_cust_property)
    # 戻り値の解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇）、REQUEST I/F、機能毎引数項目仕様」
    # p6/43 No.7 引数名:CLMKabuCancelOrder を参照してください。

    print('sResultCode= ', json_return.get('sResultCode'))  # 業務処理.エラーコード 0:正常、5桁数字:「結果テキスト」に対応するエラーコード
    print('sResultText= ', json_return.get('sResultText'))
    
    

    print()
    print('-- 注文約定一覧 -------------------------------------------------------------')
    # 
    req_item = [class_req()]    # 初期化
    
    str_sIssueCode = my_code     # ''：指定なし の場合全注文を取得する。プログラム最初のパスワード設定の下の行で設定した銘柄コード
    int_p_no = int_p_no + 1
    # 注文一覧取得
    json_return = func_get_order_list(int_p_no, str_sIssueCode, class_cust_property)
    # 戻り値の解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇）、REQUEST I/F、機能毎引数項目仕様」
    # p12-14/43 No.13 引数名:CLMOrderList 1-42 を参照してください。
        
    print('oderlist= ')
    
    dic_return = json_return.get('aOrderList')
    # 複数行の注文データが返るとjsonデータがネストする
    print('len(dic_return)= ', len(dic_return))     # 取得データ件数
            
    for i in range(len(dic_return)):
        print(dic_return[i].get('sOrderOrderNumber'))               # 注文番号
        print(json_return['aOrderList'][i]['sOrderIssueCode'])      # 銘柄コード
        print(json_return['aOrderList'][i]['sOrderBaibaiKubun'])    # 売買
        print(json_return['aOrderList'][i]['sOrderOrderPrice'])     # 価格
        print(json_return['aOrderList'][i]['sOrderOrderSuryou'])    # 株数
        print(json_return['aOrderList'][i]['sOrderStatusCode'])     # 注文状態コード
        print(json_return['aOrderList'][i]['sOrderStatus'])         # 注文状態
        print()



    
    print()
    print('-- logout -------------------------------------------------------------')
    ## マニュアルの解説「（２）ログアウト」
    ##        {
    ##　　　　　"p_no":"2",
    ##　　　　　"p_sd_date":"2020.07.01-10:00:00.100",
    ##　　　　　"sCLMID":"CLMAuthLogoutRequest"
    ##　　　　}
    ##
    ##　　　要求例：
    ##　　　　仮想ＵＲＬ（REQUEST）/?{"p_no":"2","p_sd_date":"2020.07.01-10:00:00.100","sCLMID":"CLMAuthLogoutRequest"}

    # 送信項目の解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇）、REQUEST I/F、機能毎引数項目仕様」
   # p3/43 No.3 引数名:CLMAuthLogoutRequest を参照してください。
    
    int_p_no = int_p_no + 1
    bool_logout = func_logout(int_p_no, class_cust_property)
   
else :
    print('ログインに失敗しました')
