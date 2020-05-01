import requests
import json
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
        'cache-control': "no-cache"
        }

    response = requests.request("POST", url, data=payload, headers=headers)
    merchants = dict()
    for merchant in response.json()['data']:
        merchants[merchant['store_name']]=merchant['user_id']
    return merchants

def get_category_name(user_id,catalogue_id):
    payload             = { "api_key"            :"aafb702727d770509efb0b2e7576ce4f",
                            "user_id"            :user_id,
                            "marketplace_user_id":157755,
                            "catalogue_id"       :catalogue_id
                          }
    body                = json_to_string(payload)
    headers             = {'Content-Type': "application/json",'cache-control': "no-cache"}
    response            = requests.request("POST", "https://api.yelo.red/open/catalogue/get", data=body, headers=headers)
    json1               = json.loads(response.text)   
    return get_category(user_id,catalogue_id)['data']['result'][0]['name']

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
        body["multi_image_url"] = [image_url]

    headers = {
             "Content-Type"      : "application/json",
             "cache-control"     : "no-cache"
             }
    
    print(json_to_string(body))

    try:
        #url = "https://beta-api.yelo.red/open/product/edit"
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
        payload["multi_image_url"]       = [image_url]
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

def concat_images(*args):
    if len(args)==1:
        return list(args)
    else:
        return [i for i in args]