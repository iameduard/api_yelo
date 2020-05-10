#!/usr/bin/python3
# coding: utf-8
import warnings
warnings.filterwarnings('ignore')
import json
import csv
import requests
import os.path
import oauth2client
import gspread
import json
import sys
from   oauth2client.service_account import ServiceAccountCredentials
from bs4 import BeautifulSoup, NavigableString
from api_yelo import get_all_merchants
from api_yelo import json_to_string
from api_yelo import get_catalog
from api_yelo import update_product
from api_yelo import disable_product
from api_yelo import delete_product
from api_yelo import get_all_products
from api_yelo import get_product
from api_yelo import get_category_name
from api_yelo import concat_images
from api_yelo import chang1
#######################################################
# Step 0: Share Google Drive Worksheet to this email ..
#######################################################
#'client_email': "kiwua-525@wikua-273003.iam.gserviceaccount.com"
#######################################################
# Step 1: Read Google Drive Excel Worksheet ..
#######################################################
orig_stdout = sys.stdout
f = open('out_'+date.today().strftime("%Y_%a")+'.txt', 'a')
sys.stdout = f
########################################################
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('creds02.json', scope)
client = gspread.authorize(creds)
sheet_victor_antiveros = client.open('codifica').worksheet('VictorAntivero')
api_key             = 'aafb702727d770509efb0b2e7576ce4f'
marketplace_user_id = 157755
user_id             = int(get_all_merchants().get("Víctor Antivero"))
merchants=get_all_merchants()
# delete_product(product_id=3894030,user_id=user_id)
# delete_product(product_id=3894039,user_id=user_id)
# delete_product(product_id=3894080,user_id=user_id)
merchant_to_set_markup = dict()
merchant_to_set_markup[merchants['PIAZZA Automercados']]   = 1.08
merchant_to_set_markup[merchants['Distribuidora TT']]      = 1.08
merchant_to_set_markup[merchants['El Huerto de Altamira']] = 1.08
merchant_to_set_markup[merchants['Víctor Antivero']]       = 1.15
merchant_to_set_markup[merchants['Disjobel']]              = 1.15
merchant_to_set_markup
user_bs_dollar = {
 'Víctor Antivero': 318980}
url_bcv='http://www.bcv.org.ve/estadisticas/tipo-de-cambio'
def concat_images(*args):
    if len(args)==1:
        return list(args)
    else:
        return [i for i in args]

def verify_insert_conditions(category_id,price,description,image_url):
    if(category_id!=None) and (price>0.1):
        resp = True
    else:
        resp = False
    return resp

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
        body["multi_image_url"] = [image_url]

    headers = {
             "Content-Type"      : "application/json",
             "cache-control"     : "no-cache"
             }
    
    try:
        url = "https://api.yelo.red/open/product/edit"
        response = requests.post(url     = url,
                                 data    = json_to_string(body),
                                 headers = headers)
        print('update:',response.json())
        print('-'*80)
        return 0
    except:
        return 1
    
def insert_product(user_id, name, price, category_id,image_url, description=None, long_description=None):
    payload = dict()
    payload["api_key"]               = "aafb702727d770509efb0b2e7576ce4f"
    payload["user_id"]               = user_id
    payload["marketplace_user_id"]   = 157755
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
    print('insert\n',body.replace('\'','\"'))
    headers  = {'Content-Type': "application/json",'cache-control': "no-cache"}
    try:
        response = requests.request("POST",
                                    "https://api.yelo.red/open/product/add", 
                                    data=body, 
                                    headers=headers)
        print('insert:',name,response.json())
        print('\n'+'-'*80)
        return 0
    except:
        return 1

html      = requests.get(url_bcv).text
soup      = BeautifulSoup(html)
tasa=soup.find('div',{'id':'dolar'})
tasa_cambio_bs_dollar = float(tasa.strong.text.replace(' ','').replace('.','').replace(',','.'))
categorias_victor_antiveros = get_catalog(user_id=user_id)
categorias_victor_antiveros
products_kiwua = get_all_products(user_id)
###############################################
# Step 2. Update products in kiwua...
###############################################
products = sheet_victor_antiveros.get_all_records()
factor   = merchant_to_set_markup[merchants['Víctor Antivero']]
cont1=0
cont2=0
for product in products:
        name             = product['Nombre Kiwua']
        category_id      = categorias_victor_antiveros.get(product['Categoría Kiwua'])
        price            = float(product['Precio (Convenio 01)'].replace('.','').replace(',','.'))
        price            = price/tasa_cambio_bs_dollar
        price            = round(price*factor,2)
        description      = product['Descripción Kiwua (Presentación)']
        long_description = product['Descripción Larga Kiwua (Beneficio & usos)']
        image_url        = concat_images(product['URL Imagen 1'],
                                         product['URL Imagen 2'],
                                         product['URL Imagen 3'],
                                         product['URL Imagen 4'],
                                         product['URL Imagen 5'],
                                         product['URL Imagen 6'])
        resp1 = 1
        resp2 = 1
        try:
            product_id  = products_kiwua[chang1(name)][0]
            disable_product(user_id,[product_id],1)
            resp1       = update_product(  user_id      = user_id
                                           ,product_id  = product_id
                                           ,name        = name
                                           ,price       = price
                                           ,image_url   = image_url
                                           ,description = description)
            if resp1==0:
                cont1+=1
        except KeyError:
            if verify_insert_conditions(category_id,price,description,image_url):
                resp2 = insert_product(user_id          = user_id, 
                                       category_id      = category_id,
                                       name             = name,
                                       price            = price,
                                       description      = description,
                                       long_description = long_description,
                                       image_url        = image_url)
            else:
                print('Register imcomplete',[category_id,price,description,image_url])
            if resp2==0:
                cont2+=1
print('Updated :',cont1,' records')
print('Inserted:',cont2,' records')
sys.stdout = orig_stdout
f.close()
