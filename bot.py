import discord
import requests
import os
from threading import Thread
from http.server import SimpleHTTPRequestHandler, HTTPServer

# ======================
# Servidor web "keep-alive" para Render
# ======================
def run_server():
    port = int(os.getenv("PORT", 10000))  # Render seta a variável PORT
    server = HTTPServer(("0.0.0.0", port), SimpleHTTPRequestHandler)
    print(f"Servidor keep-alive rodando na porta {port}")
    server.serve_forever()

# Rodar servidor em background
Thread(target=run_server, daemon=True).start()

# ======================
# Bot Discord
# ======================
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
N8N_WEBHOOK_URL = os.getenv('N8N_WEBHOOK_URL')
CANAL_ID = int(os.getenv('CANAL_ID'))

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'✅ Bot conectado como {client.user}')
    print(f'👀 Monitorando canal ID: {CANAL_ID}')
    print('🤖 Bot online!')

@client.event
async def on_message(message):
    # Não responder a si mesmo
    if message.author == client.user:
        return
    
    # Só processar mensagens do canal específico
    if message.channel.id != CANAL_ID:
        return
    
    # Só processar comandos !rota
    if not message.content.startswith('!rota'):
        return
    
    print(f'📩 Comando recebido: {message.content}')
    
    # Preparar dados para enviar ao n8n
    payload = {
        'content': message.content,
        'channel_id': str(message.channel.id),
        'author': {
            'id': str(message.author.id),
            'username': message.author.name
        }
    }
    
    try:
        # Enviar para n8n
        response = requests.post(N8N_WEBHOOK_URL, json=payload, timeout=10)
        print(f'➡️ Enviado para n8n - Status: {response.status_code}')
        
        if response.status_code == 200:
            print('✅ Sucesso!')
        else:
            print(f'❌ Erro no n8n: {response.text}')
            
    except requests.exceptions.RequestException as e:
        print(f'⚠️ Erro ao enviar para n8n: {e}')

if __name__ == "__main__":
    print('🚀 Iniciando bot Discord...')
    client.run(DISCORD_TOKEN)
