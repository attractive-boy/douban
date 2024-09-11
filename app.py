from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import json

moonyun = Flask(__name__)

# 用于存储订单数据的文件名
DATA_FILE = 'orders.json'

# 加载订单数据
def load_orders():
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

# 保存订单数据
def save_orders(orders):
    with open(DATA_FILE, 'w', encoding='utf-8') as file:
        json.dump(orders, file, ensure_ascii=False, indent=4)

# 加载订单数据
orders = load_orders()

@moonyun.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # 从表单中获取数据
        order = {
            'order_id': request.form.get('order_id'),
            'task_type': request.form.get('task_type'),
            'start_date': request.form.get('start_date'),
            'keyword': request.form.get('keyword'),
            'task_amount': request.form.get('task_amount'),
            'execution_count': request.form.get('execution_count'),
            'task_status': request.form.get('task_status'),
            'details': []
        }
        # 将新订单添加到订单列表
        orders.append(order)
        save_orders(orders)
        return redirect(url_for('index'))

    # 渲染页面，并传递订单数据
    return render_template('index.html', orders=orders)

@moonyun.route('/delete/<int:index>', methods=['POST'])
def delete_order(index):
    if 0 <= index < len(orders):
        del orders[index]
        save_orders(orders)
    return redirect(url_for('index'))

@moonyun.route('/update/<int:index>', methods=['GET', 'POST'])
def update_order(index):
    if request.method == 'POST':
        if 0 <= index < len(orders):
            # 更新订单数据
            orders[index] = {
                'order_id': request.form.get('order_id'),
                'task_type': request.form.get('task_type'),
                'start_date': request.form.get('start_date'),
                'keyword': request.form.get('keyword'),
                'task_amount': request.form.get('task_amount'),
                'execution_count': request.form.get('execution_count'),
                'task_status': request.form.get('task_status'),
                'details': orders[index].get('details', [])
            }
            save_orders(orders)
        return redirect(url_for('index'))
    
    # 渲染修改表单页面
    return render_template('update.html', order=orders[index], index=index)

@moonyun.route('/update_details/<int:index>', methods=['POST'])
def update_order_details(index):
    if 0 <= index < len(orders):
        details = []
        accounts = request.form.getlist('account[]')
        ip_addresses = request.form.getlist('ip_address[]')
        target_links = request.form.getlist('target_link[]')
        run_statuses = request.form.getlist('run_status[]')

        if not (len(accounts) == len(ip_addresses) == len(target_links) == len(run_statuses)):
            return "Error: Mismatched details length", 400
        
        for i in range(len(accounts)):
            detail = {
                'account': accounts[i],
                'ip_address': ip_addresses[i],
                'target_link': target_links[i],
                'run_status': run_statuses[i]
            }
            details.append(detail)
        
        orders[index]['details'] = details
        save_orders(orders)
    
    return redirect(url_for('update_order', index=index))
@moonyun.route('/orders/<int:index>', methods=['GET'])
def get_order(index):
    if 0 <= index < len(orders):
        return json.dumps(orders[index]), 200
    return "Order not found", 404
@moonyun.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    if file:
        df = pd.read_excel(file)
        details = df.to_dict(orient='records')
        
        order_id = request.form.get('order_id')
        for order in orders:
            if order['order_id'] == order_id:
                order['details'].extend(details)
                break
        else:
            new_order = {
                'order_id': order_id,
                'task_type': request.form.get('task_type'),
                'start_date': request.form.get('start_date'),
                'keyword': request.form.get('keyword'),
                'task_amount': request.form.get('task_amount'),
                'execution_count': request.form.get('execution_count'),
                'task_status': request.form.get('task_status'),
                'details': details
            }
            orders.append(new_order)
        
        save_orders(orders)
    return redirect(url_for('index'))

@moonyun.route('/add_order', methods=['POST'])
def add_order():
    global orders
    # Retrieve form data
    order = {
        'order_id': request.form.get('order_id'),
        'task_type': request.form.get('task_type'),
        'start_date': request.form.get('start_date'),
        'keyword': request.form.get('keyword'),
        'task_amount': request.form.get('task_amount'),
        'execution_count': request.form.get('execution_count'),
        'task_status': request.form.get('task_status'),
        'details': []  # Initialize with empty details list
    }
    
    # Load existing orders
    orders = load_orders()
    
    # Add new order to the list
    orders.append(order)
    
    # Save updated orders
    save_orders(orders)
    
    
    # Redirect back to the index page
    return redirect(url_for('index'))
