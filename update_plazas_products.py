# coding: utf-8
import warnings
warnings.filterwarnings('ignore')
import json
import csv
import requests
import os
import pprint
import re
import sys
import time
import unicodedata
from bs4 import BeautifulSoup, NavigableString
from datetime import date, datetime
orig_stdout = sys.stdout
now = datetime.now()
f = open('out_update_plazas_products_'+datetime.now().strftime('%Y_%m_%d_%H')+'.txt', 'a')
sys.stdout = f
print('Fecha de ejecucion del script:'+now.strftime("%Y_%m_%d_%H:%M:%S"))
home_url    = 'https://www.elplazas.com/'
suc         = '1013'
home_folder = os.path.expanduser('~')
## Functions definitios...
def json_to_string(dic):
    def leerArregloStrs(valor):
        s1 = ""
        esc = '"'
        for e in valor:
            e = esc + e + esc
            s1 += s1 + e
        return "["+s1+"]"
    def leerArregloInt(valor):
        esc = '"'
        arr = []
        for e in valor:
            arr.append(e)
        return "["+s1+"]"
    s1  = []
    esc = '"'
    for items in dic.items():
        clave=''
        valor=''
        clave=items[0]
        valor=items[1]
        if (type(valor)==str):
            valor= esc+valor+esc
        if (type(valor)==dict):
            valor = json_to_string(valor)
        if (type(valor)==list):
            if valor[0]==str:
                valor = leerArregloStrs(valor)
            if valor[0]==int:
                valor = leerArregloInt(valor)
        s1.append(esc + clave + esc + ":"+str(valor))
    s2 = "{"+",".join(s1)+"}"
    return  s2.replace('\'','\"')
def get_all_merchants():
    url = "https://api.yelo.red/open/marketplace/getMerchantList"
    payload = "{\n    \"api_key\": \"aafb702727d770509efb0b2e7576ce4f\",\n    \"marketplace_user_id\": 157755,\n    \"start\": 0,\n    \"length\": 100,\n    \"sortCol\": 1\n}"
    headers = {
        'Content-Type': "application/json",
        'cache-control': "no-cache",
        'Postman-Token': "2850d28f-e722-4535-a14f-dc7af7b39573"
        }
    response = requests.request("POST", url, data=payload, headers=headers)
    merchants = dict()
    for merchant in response.json()['data']:
        merchants[merchant['store_name']]=merchant['user_id']
    return merchants

def get_catalog(user_id):
    #Marketplace Kiwua
    marketplace_user_id = 157755
    #Proveedor user_id
    payload             = { "api_key"            :"aafb702727d770509efb0b2e7576ce4f",
                            "user_id"            :user_id,
                            "marketplace_user_id":marketplace_user_id
                          }
    body                = json_to_string(payload)
    headers             = {'Content-Type': "application/json",'cache-control': "no-cache"}
    response            = requests.request("POST", "https://api.yelo.red/open/catalogue/getAll", data=body, headers=headers)
    json1               = json.loads(response.text)
    cat_dic={}
    for cat in json1['data']['result']:
        cat_dic[cat['name']]=int(cat['catalogue_id'])
    
    return cat_dic

def chang1(str_):
    return str_.replace(' ','').upper()

def update_product(user_id,product_id,name,price,image_url=None,description=None):
    body=dict()
    body["api_key"]             = "aafb702727d770509efb0b2e7576ce4f"
    body["marketplace_user_id"] = 157755
    body["user_id"]             = user_id
    body["product_id"]          = product_id
    body["name"]                = name
    body["price"]               = price
    if description!=None: 
        body["description"]     = description
    if image_url!=None:
        body["multi_image_url"] = image_url

    headers = {
             "Content-Type"      : "application/json",
             "cache-control"     : "no-cache"
             }
    
    print(json_to_string(body))

    try:
        url = "https://api.yelo.red/open/product/edit"
        response = requests.post(url     = url,
                                 data    = json_to_string(body),
                                 headers = headers)
        print('update',response.json())
        print('-'*80)
        return 0
    except:
        return 1

def get_product(product_id,user_id):
    body={
            "api_key"            : "aafb702727d770509efb0b2e7576ce4f",
            "product_id"         : product_id,
            "user_id"            : user_id,
            "marketplace_user_id": 157755
    }
    headers = {
    'Content-Type': "application/json",
    'cache-control': "no-cache"
    }
    
    response = requests.post(url="https://api.yelo.red/open/product/get",
                             data=json_to_string(body), headers=headers)
    return response.json()

def get_all_products(user_id):
    limit   = 50.
    catalogo_plazas = get_catalog(user_id)
    products = dict()
    for id_category in catalogo_plazas.values():
        cont    = 0
        while(True):
            payload = {
                        "api_key"            : "aafb702727d770509efb0b2e7576ce4f",
                        "marketplace_user_id": marketplace_user_id,
                        "user_id"            : user_id,
                        "limit"              : limit,
                        "offset"             : cont*limit,
                        "parent_category_id" : id_category
                    }
            headers = {
                'Content-Type': "application/json",
                'cache-control': "no-cache,no-cache"
                }

            response = requests.request("POST", "https://api.yelo.red/open/catalogue/products", 
                                        data=json_to_string(payload), headers=headers)
            cont += 1
            #Get the products...
            if response.json()['data']['result']==[]:
                break 
            for data in response.json()['data']['result']:
                products[chang1(data['name'])]=[data['product_id'],data['name'],float(data['price'])]
    return products

def get_links(url,params):
    html      = requests.get(url, params=params).text
    soup      = BeautifulSoup(html)
    all_links = []
    for enlace in soup.find("div",{"class":"ContainerPager"}).find('div').findAll("a"):
        all_links.append(home_url+enlace.get('href'))
    return all_links

def disable_product(user_id,products_id,is_enabled):
    payload  = {
                "api_key"            : "aafb702727d770509efb0b2e7576ce4f",
                "marketplace_user_id": 157755,
                "user_id"            : user_id,
                "product_ids"        : products_id,
                "is_enabled"         : is_enabled
              }
    headers = {
                'Content-Type': "application/json",
                'cache-control': "no-cache"
              }
    body=json_to_string(payload)
    print(body)
    response = requests.request("POST", "https://api.yelo.red/open/product/disable", 
                                data=body, headers=headers)
    print(response.text)
    
def delect_product(user_id,product_id):
    marketplace_user_id = 157755
    payload             = { "api_key"            : "aafb702727d770509efb0b2e7576ce4f",
                            "marketplace_user_id": 157755,
                            "user_id"            : user_id,   
                            "product_id"         : product_id
                          }
    body                = json_to_string(payload)
    headers             = {'Content-Type': "application/json",'cache-control': "no-cache"}
    response            = requests.request("POST", "https://api.yelo.red/open/product/delete", 
                                           data=body, headers=headers)
    json1               = json.loads(response.text)
    print(json1)

def insert_product(user_id, name, price, category_id,image_url=None, description=None, long_description=None):
    payload = dict()
    payload["api_key"]               = "aafb702727d770509efb0b2e7576ce4f"
    payload["user_id"]               = user_id
    payload["marketplace_user_id"]   = marketplace_user_id
    payload["name"]                  = name
    payload["name_json"]             = {"es": name}
    if description!=None:
        payload["description"]           = description
        payload["description_json"]      = {"es": description}
    if long_description!=None:
        payload["long_description_json"] = {"es": long_description}
    payload["parent_category_id"]    = category_id
    if image_url!=None:
        payload["multi_image_url"]       = image_url
    payload["inventory_enabled"]     = 0
    payload["available_quantity"]    = 100
    payload["price"]                 = price
    body     = json_to_string(payload)
    print(body.replace('\'','\"'))
    headers  = {'Content-Type': "application/json",'cache-control': "no-cache"}
    try:
        response = requests.request("POST",
                                    "https://api.yelo.red/open/product/add", 
                                    data=body, 
                                    headers=headers)
        print('insert',name,response.text[0:18])
        print('\n'+'-'*80)
        return 0
    except:
        return 1
    
def find_iva(product):
    try:
        return product.find('div',{'class': 'Price'}).find("p").text.replace(',','')
    except:
        return ''
    
def exist_in_plazas(name,plazas):
    for product in plazas:
        if name == product[2]:
            return True
    return False

def tasa_cambio_bs_dollar():
    url_bcv   ='http://www.bcv.org.ve/estadisticas/tipo-de-cambio'
    html      = requests.get(url_bcv).text
    soup      = BeautifulSoup(html)
    tasa=soup.find('div',{'id':'dolar'})
    tasa_cambio_bs_dollar = float(tasa.strong.text.replace(' ','').replace('.','').replace(',','.'))
    return tasa_cambio_bs_dollar

api_key             = 'aafb702727d770509efb0b2e7576ce4f'
marketplace_user_id = 157755
user_id             = int(get_all_merchants().get("PIAZZA Automercados"))
plazas_category_links=[ {'link':'Products.php?cat=01W&suc=1013', 'cat':'Frutas y Verduras'}
                       ,{'link':'Products.php?cat=02W&suc=1013', 'cat':'Refrigerados y Congelados'}
                       ,{'link':'Products.php?cat=03W&suc=1013', 'cat':'Víveres'}
                       ,{'link':'Products.php?cat=04W&suc=1013', 'cat':'Cuidado Personal y Salud'}
                       ,{'link':'Products.php?cat=05W&suc=1013', 'cat':'Limpieza'}
                       ,{'link':'Products.php?cat=06W&suc=1013', 'cat':'Licores'}
                       ,{'link':'Products.php?cat=07W&suc=1013', 'cat':'Mascotas'}
                       ,{'link':'Products.php?cat=08W&suc=1013', 'cat':'Hogar y Temporada'}
                       ,{'link':'Products.php?cat=09W&suc=1013', 'cat':'Gourmet'}
                       ]
#Generate all links from http://www.elplazas.com..
all_links=[]
cont=0
for cat in plazas_category_links:
    url        = home_url + cat['link']
    url_short  = url.split('?')[0]
    params     = [tuple(parm.split('=')) for parm in url.split('?')[1].split('&')]
    try:
        all_links += [{'cat':cat['cat'],'links':get_links(url_short,params)}]
    except:
        pass
catalogo_plazas = get_catalog(get_all_merchants().get("PIAZZA Automercados"))
#Get all Plazas's products in http://www.elplazas.com...
products_plazas=[]
for cat_link in all_links:
    for link in cat_link['links']:
        url_short  = link.split('?')[0]
        params     = [tuple(parm.split('=')) for parm in link.split('?')[1].split('&')]
        html       = requests.get(url_short, params=params).text
        soup       = BeautifulSoup(html)
        myproducts = soup.findAll("div", {"class": "Product"})
        for product in myproducts:
            image_url   = home_url+re.sub('^./','',product.find('img', src=True).get('src'))
            name        = product.find('div',{'class': 'Description'}).find("p").text.replace('  ','').replace('\n','').replace('\r','')
            price       = float(product.find('div',{'class':'Price'}).text.replace('\n','').split('+')[-1].replace('IVA','').replace('(E)','').replace(',',''))
            description = find_iva(product)
            products_plazas.append([catalogo_plazas[cat_link['cat']],image_url,name,description,price])

products_kiwua = get_all_products(user_id)
#############################################################
# STEP 1: Disabled kiwua products not in plaza web site...
#############################################################
for kiwua in products_kiwua.values():
    name=kiwua[1]
    if not exist_in_plazas(name,products_plazas):
        product_id=kiwua[0]
        disable_product(user_id,[product_id],0)

merchant_to_set_markup = dict()
merchant_to_set_markup[get_all_merchants()['PIAZZA Automercados']]   = 1.08
merchant_to_set_markup[get_all_merchants()['Distribuidora TT']]      = 1.08
merchant_to_set_markup[get_all_merchants()['El Huerto de Altamira']] = 1.08
merchant_to_set_markup[get_all_merchants()['Víctor Antivero']]       = 1.15
merchant_to_set_markup[get_all_merchants()['Disjobel']]              = 1.15
merchant_to_set_markup
################################################
#STEP 2: Update products plaza's price...
################################################
cont    = 0
tasa    = tasa_cambio_bs_dollar()
factor  = merchant_to_set_markup[get_all_merchants()['PIAZZA Automercados']]
for row in products_plazas:
    name        = row[2]
    price       = round((row[4]/tasa)*factor,2)
    category_id = row[0]
    image_url   = row[1]
    description = row[3]
    print(name,'|',price,'|',category_id,'|',image_url,'|',description)
    resp1 = 1
    resp2 = 1
    try:
        product_id  = products_kiwua[chang1(name)][0]
        disable_product(user_id,[product_id],1)
        resp1       = update_product(  user_id      = user_id
                                       ,product_id  = product_id
                                       ,name        = name
                                       ,price       = price
                                       ,image_url   = [image_url]
                                       ,description = description)
        if resp1==0:
            cont+=1
    except KeyError:
        resp2       = insert_product(  user_id    = user_id
                                       ,name       = name
                                       ,price      = price
                                       ,category_id= category_id
                                       ,image_url  = [image_url]
                                       ,description= description)
        if resp2==0:
            cont+=1
print('Numero de registros procesador:',cont)
print('Fecha de finalizacion del script:'+now.strftime("%Y_%m_%d_%H:%M:%S"))
sys.stdout = orig_stdout
f.close()

