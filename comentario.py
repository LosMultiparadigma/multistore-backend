from flask import Flask, jsonify, request, send_from_directory
import asyncio
from prisma import Prisma

# En el archivo comment_operations.py
async def create_comment(prisma, data):
    await prisma.connect()
    comment = await prisma.comment.create(
        data={
            'text': data['text'],
            'product': {
                'connect': {
                    'id': data['product_id']
                }
            }
        }
    )
    await prisma.disconnect()
    return comment

async def get_comments_for_product(prisma, product_id):
    comments = await prisma.comment.find_many(where={'product_id': product_id})
    return [comment.model_dump() for comment in comments]

