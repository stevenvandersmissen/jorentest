#!/usr/bin/env python3
import os, json, mimetypes, smtplib
from email.message import EmailMessage
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse

class Handler(SimpleHTTPRequestHandler):
    def do_POST(self):
        if urlparse(self.path).path != '/api/contact':
            self.send_error(404); return
        try:
            length=int(self.headers.get('Content-Length','0'))
            data=json.loads(self.rfile.read(length).decode('utf-8'))
            name=str(data.get('name','')).strip(); email=str(data.get('email','')).strip(); message=str(data.get('message','')).strip()
            if not name or not email or not message: raise ValueError('Vul alle velden in.')
            # Configure SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD and CONTACT_TO in production.
            host=os.getenv('SMTP_HOST')
            if host:
                msg=EmailMessage(); msg['Subject']=f'Nieuwe fotografie-aanvraag van {name}'; msg['From']=os.getenv('SMTP_FROM',email); msg['To']=os.getenv('CONTACT_TO','info@jorenvanutterbeeck.be'); msg['Reply-To']=email; msg.set_content(f'Naam: {name}\nE-mail: {email}\n\n{message}')
                with smtplib.SMTP(host,int(os.getenv('SMTP_PORT','587'))) as smtp:
                    smtp.starttls(); smtp.login(os.getenv('SMTP_USER',''),os.getenv('SMTP_PASSWORD','')); smtp.send_message(msg)
                result={'ok':True,'message':'Bedankt — je bericht is verzonden.'}
            else:
                result={'ok':True,'message':'Bericht ontvangen. Configureer SMTP op de server om het automatisch door te sturen.'}
            body=json.dumps(result).encode()
            self.send_response(200); self.send_header('Content-Type','application/json'); self.send_header('Content-Length',str(len(body))); self.end_headers(); self.wfile.write(body)
        except Exception as e:
            body=json.dumps({'ok':False,'message':str(e)}).encode(); self.send_response(400); self.send_header('Content-Type','application/json'); self.send_header('Content-Length',str(len(body))); self.end_headers(); self.wfile.write(body)
    def log_message(self, format, *args): pass

if __name__=='__main__':
    port=int(os.getenv('PORT','4173')); print(f'Photography site running on http://0.0.0.0:{port}')
    ThreadingHTTPServer(('0.0.0.0',port),Handler).serve_forever()
