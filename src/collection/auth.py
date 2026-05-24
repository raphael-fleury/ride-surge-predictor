import os
import time
import smtplib
from email.message import EmailMessage
from src.env import UBER_EMAIL, SMTP_SERVER, SMTP_PORT, SMTP_USER, SMTP_PASS

def notify_user_login_required():
    
    if not UBER_EMAIL or not SMTP_USER or not SMTP_PASS:
        print("| [Aviso] Configurações de SMTP não encontradas no .env. Email de notificação ignorado.")
        return

    try:
        msg = EmailMessage()
        msg.set_content("A sessão do Uber expirou.\n\nPor favor, vá na máquina onde o script roda e insira o código manual na janela do navegador para renovar por mais 180 dias.")
        msg['Subject'] = 'Ação Necessária: Sessão Uber Expirada'
        msg['From'] = SMTP_USER
        msg['To'] = UBER_EMAIL
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)
        server.quit()
        print(f"| Email enviado para {UBER_EMAIL} com sucesso!")
    except Exception as e:
        print(f"| Erro ao enviar email: {e}")

def login_uber(page, context, cookies_file):
    print("\n| [!AÇÃO NECESSÁRIA!] Sessão expirada detectada.")
    notify_user_login_required()
    page.goto("https://m.uber.com/sign-in", timeout=60000)
    
    email = UBER_EMAIL or ""
    if email:
        try:
            page.fill('input[name="USERNAME"]', email)
            page.click('button#forward-button')
        except: pass

    print("| Aguardando login manual... (O script continua sozinho ao terminar)")
    page.wait_for_url(lambda url: "sign-in" not in url and "login" not in url and "auth" not in url, timeout=0)
    print("| Login concluído! Salvando nova sessão...")
    time.sleep(3)
    context.storage_state(path=cookies_file)
