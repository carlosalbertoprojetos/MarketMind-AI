#!/usr/bin/env python3
"""
MarketingAI - Script de lembretes para campanhas agendadas.
Uso: python scripts/check-reminders.py [BASE_URL] [JWT_TOKEN]
Chama GET /campaign/upcoming?hours=24 e, para cada campanha, pode enviar notificação
e POST /campaign/{id}/remind. Configure env REMINDER_EMAIL_URL ou integre com SendGrid etc.
"""
import os
import sys
import urllib.request
import json

def main():
    base = (sys.argv[1] if len(sys.argv) > 1 else os.environ.get("MARKETINGAI_API_URL", "http://localhost:8000")).rstrip("/")
    token = sys.argv[2] if len(sys.argv) > 2 else os.environ.get("JWT_TOKEN")
    if not token:
        print("Uso: check-reminders.py [BASE_URL] [JWT_TOKEN] ou defina JWT_TOKEN e opcionalmente MARKETINGAI_API_URL")
        sys.exit(1)
    req = urllib.request.Request(
        f"{base}/campaign/upcoming?hours=24",
        headers={"Authorization": f"Bearer {token}"},
    )
    with urllib.request.urlopen(req) as r:
        campaigns = json.loads(r.read().decode())
    if not campaigns:
        print("Nenhuma campanha agendada nas próximas 24h.")
        return
    for c in campaigns:
        print(f"Lembrete: campanha '{c['title']}' agendada para {c.get('schedule')} (plataforma: {c.get('platform')})")
        # Aqui: enviar e-mail/push (ex: requests.post(REMINDER_EMAIL_URL, json={...}))
        remind_req = urllib.request.Request(
            f"{base}/campaign/{c['id']}/remind",
            data=b"",
            method="POST",
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        )
        try:
            urllib.request.urlopen(remind_req)
            print("  -> Lembrete marcado como enviado.")
        except Exception as e:
            print("  -> Erro ao marcar lembrete:", e)

if __name__ == "__main__":
    main()
