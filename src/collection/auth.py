import os
import time
import smtplib
from email.message import EmailMessage

def notify_user_login_required():
    uber_email = os.environ.get("uber_email")
    smtp_server = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.environ.get("SMTP_PORT", 587))
    smtp_user = os.environ.get("SMTP_USER")
    smtp_pass = os.environ.get("SMTP_PASS")
    
    if not uber_email or not smtp_user or not smtp_pass:
        print("| [Aviso] Configurações de SMTP não encontradas no .env. Email de notificação ignorado.")
        return

    try:
        msg = EmailMessage()
        msg.set_content("A sessão do Uber expirou.\n\nPor favor, vá na máquina onde o script roda e insira o código manual na janela do navegador para renovar por mais 180 dias.")
        msg['Subject'] = 'Ação Necessária: Sessão Uber Expirada'
        msg['From'] = smtp_user
        msg['To'] = uber_email
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.send_message(msg)
        server.quit()
        print(f"| Email enviado para {uber_email} com sucesso!")
    except Exception as e:
        print(f"| Erro ao enviar email: {e}")

def login_uber(page, context, cookies_file):
    print("\n| [!AÇÃO NECESSÁRIA!] Sessão expirada detectada.")
    notify_user_login_required()
    page.goto("https://m.uber.com/sign-in", timeout=60000)
    
    email = os.environ.get("uber_email", "")
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
