from flask import Flask, jsonify, request
import asyncio
from prisma import Prisma
from comentario import create_comment, get_comments_for_product

# import os
# from supabase import create_client, Client

# url: str = os.environ.get("SUPABASE_URL")
# key: str = os.environ.get("SUPABASE_KEY")
# supabase: Client = create_client(url, key)


app = Flask(__name__)
prisma = Prisma(auto_register=True)
loop = asyncio.get_event_loop()
loop.run_until_complete(prisma.connect())


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


async def create_product(data):
    await prisma.connect()
    product = await prisma.product.create(
        data={
            'name': data['name'],
            'description': data.get('description', ''),
            'price': data['price'],
            'user': {
                'connect': {
                    'id': data['user_id']
                }
            }
        }
    )
    await prisma.disconnect()
    return product


async def get_users():
    users = await prisma.user.find_many()
    return [user.model_dump() for user in users]  # Convert each user to a dictionary


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
    data = request.get_json()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    product = loop.run_until_complete(create_product(data))
    return jsonify({
        'id': product.id,
        'name': product.name,
        'description': product.description,
        'price': product.price,
        'user_id': product.user_id
    })

@app.route('/product/<int:id>', methods=['GET'])
def get_product(id):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    product = loop.run_until_complete(get_product(id))
    return jsonify({
        'id': product.id,
        'name': product.name,
        'description': product.description,
        'price': product.price,
        'user_id': product.user_id
    })

# Comentarios
@app.route('/product/<int:product_id>/comments', methods=['GET'])
def get_comments(product_id):
    comments = loop.run_until_complete(get_comments_for_product(prisma, product_id))
    return jsonify({'comments': comments})

@app.route('/comment', methods=['POST'])
def add_comment():
    data = request.get_json()
    comment = loop.run_until_complete(create_comment(prisma, data))
    return jsonify({
        'id': comment.id,
        'text': comment.text,
        'product_id': comment.product_id
    })



if __name__ == '__main__':
    app.run(debug=True)