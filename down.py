

#!/usr/bin/env python3
"""
This script updates the database with data from tastycoffee.ru.
It can be run independently for testing or called from the admin panel.

Required packages:
- requests: for HTTP requests
- beautifulsoup4: for HTML parsing

You can install these packages with:
pip install requests beautifulsoup4

Pandas is optional but recommended for better performance:
pip install pandas
"""

import os
import sys
import sqlite3
import json
import urllib.request
import urllib.parse
import urllib.error
import re
import ssl
from pathlib import Path
import pandas as pd
# Check if requests is available, otherwise use urllib
REQUESTS_AVAILABLE = False
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    print("Warning: requests module not found. Using urllib (less reliable).")

# Check if BeautifulSoup is available
BS4_AVAILABLE = False
try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    print("Warning: beautifulsoup4 module not found. Using fallback HTML parser.")

# Check if pandas is available
PANDAS_AVAILABLE = False
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    print("Warning: pandas not found. Using fallback implementation.")

def main():
    """Main function to update the database"""
    # Set the working directory to the project root
    project_root = find_project_root()
    if project_root:
        os.chdir(project_root)
    
    print("Starting database update process...")
    
    try:
        # Get data from API
        if REQUESTS_AVAILABLE and BS4_AVAILABLE:
            products_data = get_data_with_requests()
        else:
            products_data = get_data_with_urllib()
            
        if not products_data:
            raise Exception("Failed to get product data")
            
        # Process data and update database
        if PANDAS_AVAILABLE:
            process_with_pandas(products_data)
        else:
            process_without_pandas(products_data)
        
        print("Database update complete.")
        return True
        
    except Exception as e:
        print(f"Error updating database: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def get_data_with_requests():
    """Get data using requests library"""
    print("Using requests library...")
    s = requests.Session()
    s.headers.update({
        'User-Agent': 'Mozilla/5.0...',
        'Accept': 'application/json',
        'Content-Type': 'application/json',  # Для JSON-запроса
        'Origin': 'https://tastycoffee.ru',
        'Referer': 'https://tastycoffee.ru/personal'
    })
    
    # Get the main page
    url = 'https://tastycoffee.ru/personal'
    res = s.get(url)
    print(f"Connection to main page: {res.status_code}")
    
    # Login data
    data = {
        'login': 'grioltula@gmail.com',
        'password': 'Uhbajy1125',
    }
    s.proxies = {'http': None, 'https': None}
    # Try login with both formats
    response = s.post('https://api.tastycoffee.ru/api/v1/auth/login', data=data)
    print(f"Login attempt with form data: {response.status_code}")
    print(str(response.text))
    # If that fails, try JSON format
    if response.status_code != 200:
        print("Trying login with JSON format...")
        response = s.post('https://api.tastycoffee.ru/api/v1/auth/login', json=data)
        print(f"Login attempt with JSON: {response.status_code}")
    
    if response.status_code != 200:
        raise Exception(f"Failed to login with both form data and JSON. Status code: {response.status_code}")
    
    # Parse response
    response_content = response.content.decode('utf-8')
    response_data = json.loads(response_content)
    
    if 'data' not in response_data:
        print(f"Response data: {response_data}")
        raise Exception("Failed to get access token. 'data' field not found in response.")
    
    if 'access_token' not in response_data['data']:
        print(f"Response data: {response_data}")
        raise Exception("Failed to get access token. 'access_token' not found in response data.")
    
    # Set authorization header
    token = response_data['data']['access_token']
    headers = {'Authorization': f"Bearer {token}"}
    
    # Get product data
    rsp = s.get('https://api.tastycoffee.ru/api/v1/catalog/products', headers=headers)
    print(f"Products data request: {rsp.status_code}")
    
    if rsp.status_code != 200:
        raise Exception(f"Failed to get products data. Status code: {rsp.status_code}")
    
    # Parse products data
    content = BeautifulSoup(rsp.content, 'html.parser').string
    products_data = json.loads(content)['data']
    return products_data

def get_data_with_urllib():
    """Fallback method to get data using urllib"""
    print("Using urllib (fallback method)...")
    
    # Create context for SSL
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    # Function to make HTTP requests
    def make_request(url, method='GET', data=None, headers=None, json_data=None):
        headers = headers or {}
        headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        
        if json_data and method == 'POST':
            # JSON data
            data = json.dumps(json_data).encode('utf-8')
            headers['Content-Type'] = 'application/json'
        elif data and method == 'POST':
            # Form data
            data = urllib.parse.urlencode(data).encode('utf-8')
            headers['Content-Type'] = 'application/x-www-form-urlencoded'
        
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        
        try:
            response = urllib.request.urlopen(req, context=ctx)
            return {
                'status': response.status,
                'content': response.read().decode('utf-8')
            }
        except urllib.error.HTTPError as e:
            return {
                'status': e.code,
                'content': e.read().decode('utf-8') if e.fp else ''
            }
    
    # Visit main page
    main_url = 'https://tastycoffee.ru/personal'
    make_request(main_url)
    
    # Login data
    login_data = {
        'login': 'grioltula@gmail.com',
        'password': 'Uhbajy1125',
    }
    
    # Try to login with form data first
    login_url = 'https://api.tastycoffee.ru/api/v1/auth/login'
    login_response = make_request(login_url, method='POST', data=login_data)
    print(f"Login attempt with form data: {login_response['status']}")
    
    # If that fails, try with JSON
    if login_response['status'] != 200:
        print("Trying login with JSON data...")
        login_response = make_request(login_url, method='POST', json_data=login_data)
        print(f"Login attempt with JSON: {login_response['status']}")
    
    if login_response['status'] != 200:
        # Debugging
        print(f"Login failed. Response content: {login_response['content']}")
        raise Exception(f"Failed to login. Status code: {login_response['status']}")
    
    # Parse the token
    try:
        response_data = json.loads(login_response['content'])
        if 'data' not in response_data or 'access_token' not in response_data['data']:
            print(f"Response data: {response_data}")
            raise Exception("Failed to get access token from response")
        
        token = response_data['data']['access_token']
        print(str(token))
    except (json.JSONDecodeError, KeyError) as e:
        raise Exception(f"Error parsing login response: {str(e)}")
    
    # Get product data
    products_url = 'https://api.tastycoffee.ru/api/v1/catalog/products'
    auth_headers = {'Authorization': f"Bearer {token}"}
    products_response = make_request(products_url, headers=auth_headers)
    
    if products_response['status'] != 200:
        raise Exception(f"Failed to get products data. Status code: {products_response['status']}")
    
    # Parse the response
    try:
        products_data = json.loads(products_response['content'])['data']
        return products_data
    except (json.JSONDecodeError, KeyError) as e:
        raise Exception(f"Error parsing products response: {str(e)}")

def process_with_pandas(products_data):
    """Process data using pandas (preferred method)"""
    print("Processing data with pandas...")
    
    # Create DataFrame from the data
    df = pd.json_normalize(products_data)
    
    # Process categories
    df1 = df.explode('offers').reset_index(drop=True)
    df1 = df1.join(pd.json_normalize(df1['offers']), rsuffix='_offer')
    
    # Create category dictionary
    cat_dct = {
        3: 'Смеси для молочных напитков', 
        5: 'Кофе без кофеина',
        6: 'Смеси для эспрессо',
        7: 'Моносорта для эспрессо',
        8: 'Микролоты для эспрессо',
        13: 'Микролоты для фильтра',
        11: 'Смеси для фильтра',
        9: 'Смеси для вендинга',
        14: 'Микролоты для фильтра 100г',
        12: 'Моносорта для фильтра',
        20: 'Черный чай',
        21: 'Зеленый чай',
        23: 'Улун',
        24: 'Черный ароматизированный чай',
        25: 'Зеленый ароматизированный чай',
        26: 'Фруктовый чай',
        27: 'Травяные смеси',
        28: 'Пуэр',
        29: 'Добавки к чаю',
        56: 'Specialty tea',
        32: 'Мерч',
        33: 'Средства для чистки',
        34: 'Аксессуары бариста',
        35: 'Одноразовая посуда',
        36: 'Аксессуары для заваривания',
        37: 'Фильтры',
        38: 'Весы',
        40: 'Кофемолки',
        42: 'Посуда',
        45: 'Сиропы Gourmix 1л',
        46: 'Сопутствующие товары для сиропов',
        47: 'Капсулы для Nespresso',
        48: 'Упаковка 10 дрип-пакетов',
        49: 'Кофе в банках',
        51: 'Upcycled мерч',
        52: 'Сахар',
        53: 'Посуда To Go',
        55: 'Кофейный концентрат 3л',
        58: 'Шоколад в порошке',
        61: 'Шоколад в плитках',
        63: 'Упаковка 5 дрип-пакетов',
        64: 'Наборы Дрип-кофе',
        69: 'Чайники',
        71: 'Упаковка 30 дрип-пакетов',
        72: 'Брю-бэги'
    }
    
    # Create category dataframe
    df_prnt = df1[['type']].drop_duplicates()
    categories = pd.DataFrame()
    categories['name'] = df_prnt.type
    categories.sort_values('name', inplace=True)
    categories.reset_index(drop=True, inplace=True)
    categories['parent_id']=0
    categories['is_hidden']=0
    categories.index+=1
    categories.reset_index(inplace=True, names=['id'])
    
    # Helper function for category ID
    def cat_id(cat):
        try:
            return cat_dct[cat]
        except:
            return cat
    
    # Process subcategories
    subcat = df1[['category_id','type']].drop_duplicates()
    subcat['name'] = subcat.apply(lambda x: cat_id(x.category_id), axis=1)
    subcat = pd.merge(categories[['name','id']], subcat, right_on='type', left_on='name')
    subcat.rename(columns = {'id':'parent_id','category_id':'id', 'name_y':'name'}, inplace = True)
    subcat['is_hidden']=0
    subcat['id']+=1
    categories = pd.concat([categories, subcat[['id','name','parent_id','is_hidden']]])
    
    # Process items
    subcat = df1[['category_id','name','id']].drop_duplicates()
    subcat.rename(columns={'category_id':'parent_id'}, inplace=True)
    subcat['is_hidden']=0
    subcat['parent_id']+=1
    subcat['id']+=10000
    categories = pd.concat([categories, subcat[['id','name','parent_id','is_hidden']]])
    
    # Replace category names
    categories.replace({'tea':'Чай','coffee':'Кофе'}, inplace=True)
    categories.fillna('Аксессуары', inplace=True)
    
    # Create items dataframe
    items = df1[['id_offer','name_offer','info.mini_description','id','price','card_product', 'weight', 'type_offer']].rename(
        columns = {'id':'category_id',
                    'id_offer':'id',
                    'name_offer':'name',
                    'info.mini_description':'description',
                    'card_product':'image_id'})
    items['is_hidden']=0
    items['category_id']+=10000
    items.sort_values('weight', ascending=False, inplace = True)
    items['name'] = items['type_offer'].combine_first(items['name'])
    items.drop('type_offer', axis=1, inplace = True)
    items['name'] = items['name'].replace('bean_coffee','кофе в зернах').replace('ground_coffee','молотый')
    
    # Save to SQLite database
    print(f"Saving data to database: {len(categories)} categories, {len(items)} items")
    db_path = "database.db"
    conn = sqlite3.connect(db_path)
    categories.to_sql('categories', con=conn, index=False, if_exists='replace')
    items.to_sql('items', con=conn, index=False, if_exists='replace')
    conn.close()

def process_without_pandas(products_data):
    """Fallback method to process data without pandas"""
    print("Processing data without pandas (fallback method)...")
    
    # Create category dictionary
    cat_dct = {
        3: 'Смеси для молочных напитков', 
        5: 'Кофе без кофеина',
        6: 'Смеси для эспрессо',
        7: 'Моносорта для эспрессо',
        8: 'Микролоты для эспрессо',
        13: 'Микролоты для фильтра',
        11: 'Смеси для фильтра',
        9: 'Смеси для вендинга',
        14: 'Микролоты для фильтра 100г',
        12: 'Моносорта для фильтра',
        20: 'Черный чай',
        21: 'Зеленый чай',
        23: 'Улун',
        24: 'Черный ароматизированный чай',
        25: 'Зеленый ароматизированный чай',
        26: 'Фруктовый чай',
        27: 'Травяные смеси',
        28: 'Пуэр',
        29: 'Добавки к чаю',
        56: 'Specialty tea',
        32: 'Мерч',
        33: 'Средства для чистки',
        34: 'Аксессуары бариста',
        35: 'Одноразовая посуда',
        36: 'Аксессуары для заваривания',
        37: 'Фильтры',
        38: 'Весы',
        40: 'Кофемолки',
        42: 'Посуда',
        45: 'Сиропы Gourmix 1л',
        46: 'Сопутствующие товары для сиропов',
        47: 'Капсулы для Nespresso',
        48: 'Упаковка 10 дрип-пакетов',
        49: 'Кофе в банках',
        51: 'Upcycled мерч',
        52: 'Сахар',
        53: 'Посуда To Go',
        55: 'Кофейный концентрат 3л',
        58: 'Шоколад в порошке',
        61: 'Шоколад в плитках',
        63: 'Упаковка 5 дрип-пакетов',
        64: 'Наборы Дрип-кофе',
        69: 'Чайники',
        71: 'Упаковка 30 дрип-пакетов',
        72: 'Брю-бэги'
    }
    
    # Extract all types
    types = set()
    for product in products_data:
        if 'type' in product:
            types.add(product['type'])
    
    # Create base categories
    categories = []
    for i, t in enumerate(sorted(types), 1):
        categories.append({
            'id': i,
            'name': t,
            'parent_id': 0,
            'is_hidden': 0
        })
    
    # Create a mapping from type name to id
    type_to_id = {c['name']: c['id'] for c in categories}
    
    # Process subcategories
    next_id = len(categories) + 1
    subcategories = []
    
    # Extract category mappings
    category_types = {}
    for product in products_data:
        if 'category_id' in product and 'type' in product:
            category_types[(product['category_id'], product['type'])] = 1
    
    # Create subcategories
    for (cat_id, type_name) in category_types:
        if type_name in type_to_id:
            cat_name = cat_dct.get(cat_id, str(cat_id))
            subcategories.append({
                'id': next_id,
                'name': cat_name,
                'parent_id': type_to_id[type_name],
                'is_hidden': 0
            })
            next_id += 1
    
    # Process items
    items = []
    for product in products_data:
        if 'offers' in product and product['offers']:
            for offer in product['offers']:
                if 'id' in offer:
                    items.append({
                        'id': offer.get('id', 0),
                        'name': offer.get('name', ''),
                        'description': product.get('info', {}).get('mini_description', ''),
                        'category_id': product.get('id', 0) + 10000,
                        'price': offer.get('price', 0),
                        'image_id': product.get('card_product', None),
                        'weight': offer.get('weight', 0),
                        'is_hidden': 0
                    })
    
    # Replace category names
    for category in categories:
        if category['name'] == 'tea':
            category['name'] = 'Чай'
        elif category['name'] == 'coffee':
            category['name'] = 'Кофе'
        elif not category['name']:
            category['name'] = 'Аксессуары'
    
    # Fix item names
    for item in items:
        if item['name'] == 'bean_coffee':
            item['name'] = 'кофе в зернах'
        elif item['name'] == 'ground_coffee':
            item['name'] = 'молотый'
    
    # Combine all categories
    all_categories = categories + subcategories
    
    # Save to SQLite database
    print(f"Saving data to database: {len(all_categories)} categories, {len(items)} items")
    db_path = "database.db"
    conn = sqlite3.connect(db_path)
    
    # Create tables if they don't exist
    conn.execute('''
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY,
        name TEXT,
        parent_id INTEGER,
        is_hidden INTEGER
    )
    ''')
    
    conn.execute('''
    CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY,
        name TEXT,
        description TEXT,
        category_id INTEGER,
        price REAL,
        image_id TEXT,
        weight INTEGER,
        is_hidden INTEGER
    )
    ''')
    
    # Clear existing data
    conn.execute('DELETE FROM categories')
    conn.execute('DELETE FROM items')
    
    # Insert categories
    for category in all_categories:
        conn.execute(
            'INSERT INTO categories (id, name, parent_id, is_hidden) VALUES (?, ?, ?, ?)',
            (category['id'], category['name'], category['parent_id'], category['is_hidden'])
        )
    
    # Insert items
    for item in items:
        conn.execute(
            'INSERT INTO items (id, name, description, category_id, price, image_id, weight, is_hidden) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
            (item['id'], item['name'], item['description'], item['category_id'], item['price'], 
             item['image_id'], item['weight'], item['is_hidden'])
        )
    
    conn.commit()
    conn.close()

def find_project_root():
    """Find the project root directory by looking for specific files."""
    current_dir = Path(os.getcwd())
    
    # Try to find project root by looking for characteristic files
    for parent in [current_dir] + list(current_dir.parents):
        if (parent / "src").exists() and (parent / "database.db").exists():
            return str(parent)
    
    return None

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 

