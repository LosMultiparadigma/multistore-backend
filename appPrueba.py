from flask import Flask, jsonify, request, send_from_directory
import asyncio
from prisma import Prisma
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
CORS(app)
#app.config['UPLOAD_FOLDER'] = 'uploads/'

prisma = Prisma(auto_register=True)
loop = asyncio.get_event_loop()
loop.run_until_complete(prisma.connect())

#if not os.path.exists(app.config['UPLOAD_FOLDER']):
    #os.makedirs(app.config['UPLOAD_FOLDER'])

# User-related functions
async def get_user():
    await prisma.connect()
    user = await prisma.user.create(
        data={
            'name': 'John Doe',
            'email': 'jadjf@jajs.com',
            'password': '123456'
        }
    )
    await prisma.disconnect()
    return user

async def create_user(data):
    user = await prisma.user.create(
        data={
            'name': data['name'],
            'email': data['email'],
            'password': data['password']
        }
    )
    return user

async def get_users():
    users = await prisma.user.find_many()
    return [user.model_dump() for user in users]  # Convert each user to a dictionary

# Product-related functions
async def create_product(data, filename=None):
    await prisma.connect()
    product_data = {
        'name': data['name'],
        'description': data.get('description', ''),
        'price': data['price'],
        'user': {
            'connect': {
                'id': data['user_id']
            }
        }
    }
    if filename:
        product_data['image'] = filename
    product = await prisma.product.create(data=product_data)
    await prisma.disconnect()
    return product

async def get_product_by_id(product_id):
    await prisma.connect()
    product = await prisma.product.find_unique(where={'id': product_id})
    await prisma.disconnect()
    return product

async def get_all_products():
    await prisma.connect()
    products = await prisma.product.find_many()
    await prisma.disconnect()
    return [product.model_dump() for product in products]

async def update_product(product_id, data, filename=None):
    await prisma.connect()
    update_data = {key: data[key] for key in data if data[key] is not None}
    if filename:
        update_data['image'] = filename
    product = await prisma.product.update(where={'id': product_id}, data=update_data)
    await prisma.disconnect()
    return product

async def delete_product(product_id):
    await prisma.connect()
    await prisma.product.delete(where={'id': product_id})
    await prisma.disconnect()
    return {'message': 'Product deleted successfully'}

# Order-related functions
async def create_order(data):
    await prisma.connect()
    order = await prisma.order.create(
        data={
            'total': data['total'],
            'userId': data['user_id']
        }
    )
    await prisma.disconnect()
    return order

async def get_orders():
    await prisma.connect()
    orders = await prisma.order.find_many()
    await prisma.disconnect()
    return [order.model_dump() for order in orders]

# Routes
@app.route('/users', methods=['GET'])
def index():
    users = loop.run_until_complete(get_users())
    return jsonify({'users': users})

@app.route('/user', methods=['POST'])
def add_user():
    data = request.get_json()
    user = loop.run_until_complete(create_user(data))
    return jsonify({
        'id': user.id,
        'name': user.name,
        'email': user.email
    })

@app.route('/product', methods=['POST'])
def add_product():
    data = request.form
    image = request.files.get('image')
    filename = None
    if image:
        filename = secure_filename(image.filename)
        image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    product = loop.run_until_complete(create_product(data, filename))
    return jsonify({
        'id': product.id,
        'name': product.name,
        'description': product.description,
        'price': product.price,
        'user_id': product.user_id,
        'image': product.image if 'image' in product else None
    })

@app.route('/product/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = loop.run_until_complete(get_product_by_id(product_id))
    if product:
        return jsonify({
            'id': product.id,
            'name': product.name,
            'description': product.description,
            'price': product.price,
            'user_id': product.user_id,
            'image': product.image if 'image' in product else None
        })
    else:
        return jsonify({'error': 'Product not found'}), 404

@app.route('/products', methods=['GET'])
def get_products():
    products = loop.run_until_complete(get_all_products())
    return jsonify(products)


@app.route('/product/<int:product_id>', methods=['PUT'])
def update_product_route(product_id):
    data = request.form
    image = request.files.get('image')
    filename = None
    if image:
        filename = secure_filename(image.filename)
        image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    product = loop.run_until_complete(update_product(product_id, data, filename))
    if product:
        return jsonify({
            'id': product.id,
            'name': product.name,
            'description': product.description,
            'price': product.price,
            'user_id': product.user_id,
            'image': product.image if 'image' in product else None
        })
    else:
        return jsonify({'error': 'Product not found'}), 404

@app.route('/product/<int:product_id>', methods=['DELETE'])
def delete_product_route(product_id):
    result = loop.run_until_complete(delete_product(product_id))
    return jsonify(result)

# Order routes
@app.route('/order', methods=['POST'])
def add_order():
    data = request.get_json()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    order = loop.run_until_complete(create_order(data))
    return jsonify({
        'id': order.id,
        'total': order.total,
        'user_id': order.user_id
    })

@app.route('/orders', methods=['GET'])
def list_orders():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    orders = loop.run_until_complete(get_orders())
    return jsonify({'orders': orders})


if __name__ == '__main__':
    app.run(debug=True)
