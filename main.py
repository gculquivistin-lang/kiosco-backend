from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class Pedido(BaseModel):
    orden: int
    items: list
    total: float

TELEGRAM_TOKEN = "8652231017:AAHQK1CrO766Lfyw9bO-tEZj5YcuVph8wFE"
CHAT_ID = "-5012907104"

# 1. Función "mensajero" que trabajará en secreto por detrás
def mandar_mensaje_telegram(mensaje: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID, 
        "text": mensaje,
        "parse_mode": "HTML"
    }
    try:
        # Le ponemos un límite de tiempo para que no se quede colgado si se va el internet
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        print(f"Error enviando a Telegram: {e}")

@app.post("/enviar-pedido")
def enviar_pedido(pedido: Pedido, background_tasks: BackgroundTasks):
    mensaje = f"🟢 <b>¡NUEVO PEDIDO!</b>\n"
    mensaje += f"🛎️ <b>ORDEN: #{pedido.orden}</b>\n\n"
    
    for item in pedido.items:
        mensaje += f"• {item['nombre']} (${item['precio']:.2f})\n"
        
    mensaje += f"\n💰 <b>TOTAL: ${pedido.total:.2f}</b>"

    # 2. Le ordenamos a Python que mande el mensaje a Telegram EN SEGUNDO PLANO
    background_tasks.add_task(mandar_mensaje_telegram, mensaje)
    
    # 3. Le respondemos a la Tablet INMEDIATAMENTE para que muestre el ticket rápido
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)