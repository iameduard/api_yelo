#!/usr/bin/python3
import warnings
warnings.filterwarnings('ignore')
import json
import csv
import requests
import os.path
import oauth2client
import gspread
import json
from   oauth2client.service_account import ServiceAccountCredentials
from bs4 import BeautifulSoup, NavigableString
from datetime import date, datetime
from api_yelo import get_all_merchants
from api_yelo import json_to_string
#from api_yelo import insert_product
from api_yelo import get_catalog
from api_yelo import update_product
from api_yelo import disable_product
from api_yelo import delete_product
from api_yelo import get_all_products
from api_yelo import get_product
from api_yelo import get_category_name
from api_yelo import concat_images
from api_yelo import chang1

orig_stdout = sys.stdout
now = datetime.now()
f = open('out_'+now.strftime("%Y_%a_%H")+'.txt', 'w')
sys.stdout = f

print('Fecha de ejecucion del script:'+now.strftime("%Y_%m_%d_%H:%M:%S"))

#######################################################
# Step 0: Share Google Drive Worksheet to this email ..
#######################################################
#No olvidar compartir la hoja de calculo con el cliente_email
#'client_email': 'catalogodtt@iconic-post-192814.iam.gserviceaccount.com'
client_email = 'kiwua-525@wikua-273003.iam.gserviceaccount.com'
get_ipython().system('cat creds02.json')
##############################################
# Step 1: Read Google Drive Excel Worksheet ..
##############################################
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('creds02.json', scope)
client = gspread.authorize(creds)
sheet_productos = client.open('Codificación Productos Kiwua').worksheet('CaribeaSea')
api_key             = 'aafb702727d770509efb0b2e7576ce4f'
marketplace_user_id = 157755
user_id             = int(get_all_merchants().get('Caribe Sea'))
merchants=get_all_merchants()
merchants
codigos={'Plaza’s':321621,
         'Subway':314801,
         'DTT':157756,
         'Huerto de Altamira':319885,
         'Nativo':267942,
         'Barco Pesca':157757,
         'INCA':308071,
         'Víctor Antivero (P&B)':318980,
         'Disjobel':157755,
         'Quick Meats':332562,
         'Monte Cacao':342619,
         'Caribe Sea':396748}

sheet_control = client.open('Control Codificación Proveedores').worksheet('Codificación')
control       = sheet_control.get_all_records()

merchant_to_set_markup = dict()
for row in control:
    if row['Margen s/costo (Eduardo)']!='':
        try:
            merchant_to_set_markup[codigos.get(row['Proveedor'])] =                         1+float(row['Margen s/costo (Eduardo)'].replace('%','').replace(',','.'))/100
        except:
            pass
print(merchant_to_set_markup)

def concat_images(*args):
    if len(args)==1:
        return list(args)
    else:
        resp= [i for i in args if i!='']
        if resp == []:
            return None
        else:
            return resp
        
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
        body["multi_image_url"] = image_url

    headers = {
             "Content-Type"      : "application/json",
             "cache-control"     : "no-cache"
             }
    
    print('update\n',json_to_string(body))

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
    
def get_all_products(user_id):
    limit   = 50
    #Buscar Todas las Categorias...
    catalogo_plazas = get_catalog(user_id)
    products = dict()
    for id_category in catalogo_plazas.values():
        cont    = 0
        while(True):
            payload = {
                        "api_key"            : "aafb702727d770509efb0b2e7576ce4f",
                        "marketplace_user_id": 157755,
                        "user_id"            : user_id,
                        "limit"              : limit,
                        "offset"             : cont*limit,
                        "parent_category_id" : id_category
                    }
            headers = {
                'Content-Type': "application/json; charset=utf-8",
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

def add_category(user_id,name,description=None,image_url=None,category_id=None):
    payload = dict()
    payload["api_key"]               = "aafb702727d770509efb0b2e7576ce4f"
    payload["marketplace_user_id"]   = 157755
    payload["user_id"]               = user_id
    payload["name"]                  = name
    payload["name_json"]             = {"es": name}
    if description!=None:
        payload["description"]           = description
        payload["description_json"]      = {"es": description}
    if category_id != None:
        payload["parent_category_id"]    = category_id
    if image_url!=None:
        payload["image_url"]         = image_url
    body                = json_to_string(payload)
    print(body)
    headers             = {'Content-Type': "application/json",'cache-control': "no-cache"}
    response            = requests.request("POST", "https://api.yelo.red/open/catalogue/add", 
                                           data=body, headers=headers)
    print(response.text)
    
def exist_in_provider(name,products):
    for product in products:
        if name == product['Nombre Kiwua']:
            return True
    return False
categorias_caribe_sea = get_catalog(user_id=user_id)
print(categorias_caribe_sea)
products_kiwua = get_all_products(user_id)
print('Products in kiwua.com')
print(products_kiwua)
products = sheet_productos.get_all_records()
print('Products in price list')
print(products)
#################################################################
# STEP 1: Disabled kiwua products not in Caribe Sea price list ...
#################################################################
products = sheet_productos.get_all_records()
for kiwua in products_kiwua.values():
    name=kiwua[1]
    if not exist_in_provider(name,products):
        product_id=kiwua[0]
        disable_product(user_id,[product_id],0)
##################################################################
# Step 2. Update products in kiwua...
##################################################################
url_bcv   = 'http://www.bcv.org.ve/estadisticas/tipo-de-cambio'
html      = requests.get(url_bcv).text
soup      = BeautifulSoup(html)

tasa=soup.find('div',{'id':'dolar'})
tasa_cambio_bs_dollar = float(tasa.strong.text.replace(' ','').replace('.','').replace(',','.'))
tasa_cambio_bs_dollar

sheet_productos = client.open('Codificación Productos Kiwua').worksheet('CaribeaSea')
products = sheet_productos.get_all_records()
products_kiwua = get_all_products(user_id)
factor   = merchant_to_set_markup[user_id]
print(f'Se aplico un markup de {factor}')
cont1=0
cont2=0
for product in products:
        name             = product['Nombre Kiwua']
        category_id      = categorias_caribe_sea.get(product['Subcategoria'])
        if category_id == None:
            #Crear la categoria
            add_category(user_id  = user_id,name=product['Subcategoria'])
            categorias_caribe_sea = get_catalog(user_id=user_id)
            category_id           = categorias_caribe_sea.get(product['Subcategoria'])
            print(f'categori_id:{category_id}')
        price            = float(product['Precio Kiwua s/markup'].replace('.','').replace(',','.'))
        price            = round(price*factor,10)
        print(price)
        description      = product['Descripción corta']
        long_description = product['Descripción larga (Caracteristicas, Beneficios, etc.)']
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
                pass
            else:
                print('Register imcomplete',[category_id,price,description,image_url])
            if resp2==0:
                cont2+=1
print('Updated :',cont1,' records')
print('Inserted:',cont2,' records')
print('Fecha de finalizacion del script:'+now.strftime("%Y_%m_%d_%H:%M:%S"))
sys.stdout = orig_stdout
f.close()