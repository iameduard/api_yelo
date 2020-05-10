#!/usr/bin/python3
import warnings
warnings.filterwarnings('ignore')
import json
import csv
import requests
import os.path
import pprint
import oauth2client
import gspread
from datetime import date, datetime
from   oauth2client.service_account import ServiceAccountCredentials
from bs4 import BeautifulSoup, NavigableString
home_folder = os.path.expanduser('~')

orig_stdout = sys.stdout
now = datetime.now()
f = open('out_'+now.strftime("%Y_%a_%H")+'.txt', 'w')
sys.stdout = f

print('Fecha de ejecucion del script:'+now.strftime("%Y_%m_%d_%H:%M:%S"))

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
        merchants[merchant['store_name'].replace(' ','').upper()]=merchant['user_id']
    return merchants

def get_catalog(user_id):
    marketplace_user_id = 157755
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
    
    print('update:\n',json_to_string(body))

    try:
        response = requests.post(url     = "https://api.yelo.red/open/product/edit",
                                 data    = json_to_string(body),
                                 headers = headers)
        print('update',response.json())
        print('-'*80)
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
                'Content-Type': "application/json",
                'cache-control': "no-cache,no-cache"
                }

            response = requests.request("POST", "https://api.yelo.red/open/catalogue/products", 
                                        data=json_to_string(payload), headers=headers)
            cont += 1           
            #print(response.json()['data']['result'])
            if response.json()['data']['result']==[]:
                break 
            for data in response.json()['data']['result']:
                products[chang1(data['name'])]=[data['product_id'],
                                                data['name'],
                                                float(data['price']),
                                                data['is_enabled']]
    return products

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

def get_all_merchants():
    url = "https://api.yelo.red/open/marketplace/getMerchantList"

    payload = "{\n    \"api_key\": \"aafb702727d770509efb0b2e7576ce4f\",\n    \"marketplace_user_id\": 157755,\n    \"start\": 0,\n    \"length\": 100,\n    \"sortCol\": 1\n}"
    headers = {
        'Content-Type': "application/json",
        'cache-control': "no-cache"
        }

    response = requests.request("POST", url, data=payload, headers=headers)
    merchants = dict()
    for merchant in response.json()['data']:
        merchants[merchant['store_name']]=merchant['user_id']
    return merchants

def insert_product(user_id, name, price, category_id,image_url=None, description=None, long_description=None):
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
    print('insert:\n',body.replace('\'','\"'))
    headers  = {'Content-Type': "application/json",'cache-control': "no-cache"}
    try:
        response = requests.request("POST",
                                    "https://api.yelo.red/open/product/add", 
                                    data=body, 
                                    headers=headers)
        print('insert',name,response.text)
        print('\n'+'-'*80)
        return 0
    except:
        return 1

def concat_images(*args):
    if len(args)==1:
        return list(args)
    else:
        resp= [i for i in args if i!='']
        if resp == []:
            return None
        else:
            return resp

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
    payload["parent_category_id"]    = category_id
    if image_url!=None:
        payload["image_url"]         = image_url
    body                = json_to_string(payload)
    headers             = {'Content-Type': "application/json",'cache-control': "no-cache"}
    response            = requests.request("POST", "https://api.yelo.red/open/catalogue/add", 
                                           data=body, headers=headers)
    #json1               = json.loads(response.text)
    print(response.text)

def verify_insert_conditions(category_id,price,description,image_url):
    if(category_id!=None) and (price>0.1):
        resp = True
    else:
        resp = False
    return resp

def exist_in_provider(name,products):
    for product in products:
        if name == product['Nombre']:
            return True
    return False

def delete_product(user_id,product_id):
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
#########################################################
api_key             = 'aafb702727d770509efb0b2e7576ce4f'
marketplace_user_id = 157755
user_id=get_all_merchants()['Disjobel']
user_id
#########################################################
# Step 1: Google Drive API...
#########################################################
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('creds02.json', scope)
client = gspread.authorize(creds)
sheet_productos = client.open('Codificación Productos Kiwua').worksheet('Disjobel')
products = sheet_productos.get_all_records()
###############################################################
# Step 2: Read Markup from Control Codificación Proveedores...
###############################################################
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
categorias_disjobel = get_catalog(user_id=user_id)
products_kiwua = get_all_products(user_id)
print(products_kiwua)
#############################################################
# Step 3: Disabled kiwua products not in Disjobel price list ...
#############################################################
products = sheet_productos.get_all_records()
for kiwua in products_kiwua.values():
    name=kiwua[1]
    if not exist_in_provider(name,products):
        product_id=kiwua[0]
        print(user_id,[name],[product_id])
        disable_product(user_id,[product_id],0)
#########################################################################################
# Step 4. Update products in kiwua and Insert whether they aren't between kiwua products...
#########################################################################################
url_bcv   = 'http://www.bcv.org.ve/estadisticas/tipo-de-cambio'
html      = requests.get(url_bcv).text
soup      = BeautifulSoup(html)

tasa=soup.find('div',{'id':'dolar'})
tasa_cambio_bs_dollar = float(tasa.strong.text.replace(' ','').replace('.','').replace(',','.'))
tasa_cambio_bs_dollar

sheet_productos = client.open('Codificación Productos Kiwua').worksheet('Disjobel')
products = sheet_productos.get_all_records()
products_kiwua = get_all_products(user_id)
factor   = merchant_to_set_markup[user_id]
print(f'Se aplico un markup de {factor}')
cont1=0
cont2=0
for product in products:
        name             = product['Nombre Kiwua']
        category_id      = categorias_disjobel.get(product['Subcategoria'])
        if category_id == None:
            add_category(user_id  = user_id,name=product['Subcategoria'])
            categorias_disjobel   = get_catalog(user_id=user_id)
            category_id           = categorias_disjobel.get(product['Subcategoria'])
            print(f'categori_id:{category_id}')
        
        price            = str(product['Precio por unidad']).replace('.','').replace(',','.')                           if product['Precio por unidad']!='' else 0
        if price == 0:
            continue
        price            = float(price)/tasa_cambio_bs_dollar
        price            = round(price*factor,6)
        price2           = price*float(str(product['Factor Precio']).replace('.','').replace(',','.'))
        description      = product['Descripción corta']
        description      = description.replace('$0,00 /','$'+str(price)+' /')
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
            resp1 = 0
            resp1       = update_product(  user_id      = user_id
                                            ,product_id  = product_id
                                            ,name        = name
                                            ,price       = price2
                                            ,image_url   = image_url
                                            ,description = description)
            if resp1==0:
                cont1+=1
        except KeyError:
            if verify_insert_conditions(category_id,price,description,image_url):
                resp2 = 0
                resp2 = insert_product(user_id          = user_id, 
                                       category_id      = category_id,
                                       name             = name,
                                       price            = price2,
                                       description      = description,
                                       long_description = long_description,
                                       image_url        = image_url)
            else:
                print('Register imcomplete',[category_id,price,description,image_url])
            if resp2==0:
                cont2+=1
print('Updated :',cont1,' records')
print('Inserted:',cont2,' records')
print('Fecha de finalizacion del script:'+now.strftime("%Y_%m_%d_%H:%M:%S"))
sys.stdout = orig_stdout
f.close()
