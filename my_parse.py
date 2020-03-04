import requests
from selenium import webdriver
from bs4 import BeautifulSoup
import json
import re

def take_num(line):
    otvet = re.findall(r'\d*\.\d+|\d+',line )
    #print(' , '.join(otvet))
    return otvet

def get_product_id(file_name = 'product_id.txt'):
    list_ids = []
    with open(file_name,'r') as ids:
        list_ids = ids.read().splitlines()
    return list_ids

def get_ptoduct_only_id():
    list_id_with_welmart = get_product_id()
    list_id = []
    for string in list_id_with_welmart:
        item = string.split('# ')
        list_id.append(item[-1])
    return list_id

def get_html_serching_products(id):
    #id = '556077407' 
    #id = '55679'
    #browser = webdriver.Chrome('c:\chromedriver_win32\chromedriver')

    url_for_search = 'https://www.walmart.com/search/'     

    query = { 
            'query' : id
            } 


    # browser.get(requests.get(url_for_search,params = query).url)   
    # content = browser.page_source
    html = requests.get(url_for_search,params = query)
    if html.status_code == 200:
        content = html.text
    else:
        content = None
    return content



# with open('t.html','w',encoding='utf-8') as w:
#     w.write(content)

# with open('s.html','r') as r:
#     html_text = r.read()



def get_product_links(content):
    links_notparse =[]
    links_parse = []
    soup = BeautifulSoup(content,'lxml')
    links_notparse = soup.find_all('div',{'class' : 'search-result-product-title listview'})

    for link in links_notparse:

        pars = link.findAll('a',href=True)
        for i in pars:
            links_parse.append(i['href'])

    print(links_parse)
    return links_parse

def scrape(link = '/ip/Acer-CB3-532-C47C-15-6-Chromebook-Chrome-OS-Intel-Celeron-N3060-Dual-Core-Processor-2GB-RAM-16GB-Internal-Storage/54518466'):
    url_for_scrape = 'https://www.walmart.com' + link
    
    page = requests.get(url_for_scrape)
    page_text = page.text
    # with open('d.html','w',encoding='utf-8') as w:
    #     w.write(page_text)
    
    return page_text,url_for_scrape

def get_product_data(data_page,self_url,product_id):

    # with open('dc.html','r',encoding='utf-8') as w:
    #     text = w.read()
    text = data_page
    data= BeautifulSoup(text,'lxml')

    
    
    product_name = data.find('h1',{'class' : 'prod-ProductTitle font-normal'})
    if product_name is not None:
        product_name = product_name.text 
    #print(product_name)
    
    product_price = data.find('div',{'class' : 'prod-PriceHero'}).find('span',{'class' : 'visuallyhidden'})
    if product_price is not None:
        product_price = product_price.text
    #print(product_price)

    product_url = self_url
    #print(product_url)
    
    product_description = data.find('div',{'class' : 'about-desc'})
    if product_description is not None:
        product_description =product_description.text
    #print(product_description)
    
    product_categoty = data.find('ol',{'class' : 'breadcrumb-list'})
    if product_categoty is not None:
        category = ''
        for i in product_categoty:
            category += i.text
        product_categoty = category
    else:
        product_categoty = 'is unknown'
    #print(product_categoty)

    product_rating = data.find('div',{'class' : 'ReviewsRating-container'})
    if product_rating  is not None:
        product_rating = product_rating.find('span',{'class' : 'stars-container'})['aria-label']
        #print(product_rating)
    else:
        product_rating = 'No rating'
        #print(product_rating)
    

    product_availability = data.find('div',{'class' : 'prod-ShippingOffer prod-PositionedRelative Grid prod-PriceHero prod-ProductOffer-enhanced'})
    if product_availability is not None:
        product_availability = product_availability.find('div',{'class' : 'Grid-col'}).find_next('div',{'class' : 'Grid-col'}).text
        if product_availability == '':
            product_availability = 'In availability'
    else:
        product_availability = 'is unknown'
    #print(product_availability)

    # product_brand = data.find_all('td' ,{'class' : 'display-name'})
    # if product_brand is not None:
    #     for i in product_brand:
    #         if 'Brand' in i.text:
    #             product_brand = i.find_next('div')
    #             product_brand = product_brand.text
    product_brand = data.find_all('tr')
    if product_brand is not None:
        for i in product_brand:
            b = i.find_next('td')
            if b.text == 'Brand':
                c = b.find_next('td')
                product_brand = c.text
                break
            
    else:
        product_brand = 'is unknown'
    #print(product_brand)
     
    product_availability_count = ' , '.join(take_num(product_availability))    
    if product_availability_count == '' or product_availability_count is None:
        product_availability_count = 'is unknown'
    #print(product_availability_count)

    delivery_price = ''
    product_delivery_price = data.find('div',{'class' : 'fulfillment-shipping-text'})
    if product_delivery_price is not  None:        
        for i in product_delivery_price:
            if not hasattr(i,'text'):
                
                delivery_price +=  i
            else:
                delivery_price +=  i.text
        product_delivery_price = delivery_price
    else:
        product_delivery_price = 'is unknown'
    #print(product_delivery_price)

    
    
    product_data = {    
    'id' : product_id,
    'name' : product_name,
    'price' : product_price,
    'url' : product_url,
    'small description': product_description,
    'category' : product_categoty,
    'rating and reviews' : product_rating,
    'availability status' : product_availability,
    'brand' : product_brand,
    'availability count' : product_availability_count,
    'delivery price' : product_delivery_price,
    }
    scrape_data_list.append(product_data)

def set_command(filename,dict):
    
    with open(filename,'w',encoding='utf-8') as p:
        json.dump(dict,p,sort_keys=False, indent=4,ensure_ascii=False)

def get_command(filename):
    with open(filename,'r') as p:
        dict = json.load(p) 
    return dict
def add_none(id_product):
    product_data = {
    id_product : 'product not found',
    }
    scrape_data_list.append(product_data)
    
#scrape_data_list = get_command('s.json')  
scrape_data_list = []

list_id = get_ptoduct_only_id()
print(list_id)
for id_product in list_id:
    content = get_html_serching_products(id_product)
    if content is None:
        add_none(id_product)
        continue
    list_links = get_product_links(content)
    if list_links == []:
        add_none(id_product)
        continue
    for link in list_links:        
        data_page,full_url = scrape(link)
        get_product_data(data_page,full_url,id_product)
        





set_command('s.json',scrape_data_list)