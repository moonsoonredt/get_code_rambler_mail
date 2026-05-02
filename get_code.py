#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import poplib
import email
from email import policy
import re
import sys
import subprocess
import html

def main():
    sys.stdout.reconfigure(encoding='utf-8')

    if len(sys.argv) < 2:
        print("ERROR: Usage: python get_code.py email:password")
        return

    conn_str = sys.argv[1]
    if ':' not in conn_str:
        print("ERROR: Format should be email:password")
        return

    user, passwd = conn_str.split(':', 1)
    domain = user.split('@')[-1].lower()

    # Автоопределение POP3-сервера
    if domain in ('mail.ru', 'inbox.ru', 'bk.ru', 'list.ru'):
        pop_server = "pop.mail.ru"
    else:
        pop_server = "pop.rambler.ru"

    srv = None
    try:
        srv = poplib.POP3_SSL(pop_server, 995, timeout=10)
        srv.user(user)
        srv.pass_(passwd)

        _, msg_list, _ = srv.list()
        if not msg_list:
            print("EMPTY: Ящик пуст или письма не загружены")
            return

        _, lines, _ = srv.retr(len(msg_list))
        raw = b'\r\n'.join(lines)
        msg = email.message_from_bytes(raw, policy=policy.default)

        # 📝 Извлекаем содержимое: сначала text/plain, потом text/html
        content = ""
        
        if msg.is_multipart():
            # 1. Пробуем найти text/plain
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    content = part.get_content()
                    if content and content.strip():
                        break
            
            # 2. Если text/plain пуст/отсутствует, берем text/html и чистим от тегов
            if not content or not content.strip():
                for part in msg.walk():
                    if part.get_content_type() == "text/html":
                        raw_html = part.get_content()
                        if raw_html:
                            # Удаляем HTML-теги и декодируем спецсимволы (&nbsp; и т.д.)
                            content = html.unescape(re.sub(r'<[^>]+>', '', raw_html))
                            break
        else:
            # Не multipart письмо
            ct = msg.get_content_type()
            payload = msg.get_content()
            if ct == "text/plain":
                content = payload
            elif ct == "text/html":
                content = html.unescape(re.sub(r'<[^>]+>', '', payload))

        if not content or not content.strip():
            print("NOTEXT: В последнем письме нет содержимого для поиска")
            return

        # 🔍 Поиск 6-значного кода
        match = re.search(r'\b(\d{6})\b', content)
        if match:
            code = match.group(1)
            print(f"CODE: {code}")
            # Автокопирование в буфер без мигания окна
            try:
                subprocess.run(['clip'], input=code.encode('utf-8'), check=True, 
                               creationflags=subprocess.CREATE_NO_WINDOW)
                print("(Скопировано в буфер обмена)")
            except Exception:
                pass
        else:
            print("NOTFOUND: 6-значный код не найден в письме")

    except poplib.error_proto as e:
        print("AUTH_ERROR: Ошибка входа. Для POP3 используйте ПАРОЛЬ ДЛЯ ВНЕШНИХ ПРИЛОЖЕНИЙ, а не основной пароль от аккаунта.")
    except Exception as e:
        print(f"ERROR: {str(e)}")
    finally:
        if srv:
            try: srv.quit()
            except: pass

if __name__ == "__main__":
    main()