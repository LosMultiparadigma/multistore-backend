from flask import Flask, jsonify, request, send_from_directory
import asyncio
from prisma import Prisma

async def create_rating(prisma, data):
    await prisma.connect()
    rating = await prisma.rating.create(
        data={
            'value': data['value'],
            'product': {
                'connect': {
                    'id': data['product_id']
                }
            }
        }
    )
    await prisma.disconnect()
    return rating

async def get_ratings_for_product(prisma, product_id):
    ratings = await prisma.rating.find_many(where={'product_id': product_id})
    return [rating.model_dump() for rating in ratings]
