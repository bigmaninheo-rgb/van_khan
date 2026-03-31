from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def handler(request):
    """Vercel serverless function handler"""
    
    try:
        # Return the main HTML file for root requests
        if request.url == '/' or request.url == '/index.html':
            index_path = ROOT / 'index.html'
            with open(index_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'text/html; charset=utf-8',
                    'Cache-Control': 'public, max-age=3600'
                },
                'body': content
            }
        
        # Serve static files
        else:
            file_path = ROOT / request.url.lstrip('/')
            if file_path.exists() and file_path.is_file():
                with open(file_path, 'rb') as f:
                    content = f.read()
                
                # Determine content type
                if file_path.suffix == '.js':
                    content_type = 'application/javascript'
                elif file_path.suffix == '.css':
                    content_type = 'text/css'
                elif file_path.suffix == '.html':
                    content_type = 'text/html; charset=utf-8'
                elif file_path.suffix in ['.png', '.jpg', '.jpeg', '.gif', '.ico']:
                    content_type = 'image/*'
                elif file_path.suffix == '.wasm':
                    content_type = 'application/wasm'
                else:
                    content_type = 'application/octet-stream'
                
                return {
                    'statusCode': 200,
                    'headers': {
                        'Content-Type': content_type,
                        'Cache-Control': 'public, max-age=31536000'
                    },
                    'body': content
                }
            else:
                return {
                    'statusCode': 404,
                    'headers': {'Content-Type': 'text/plain'},
                    'body': 'File not found'
                }
    
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'text/plain'},
            'body': f'Internal Server Error: {str(e)}'
        }
