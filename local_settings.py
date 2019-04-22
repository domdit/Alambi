import os


mail_server = "smtp.dreamhost.com"
mail_port = 465
mail_use_ssl = True
mail_address = os.getenv('EMAIL_USER')
mail_password = os.getenv('EMAIL_PASS')

recaptcha_public_key = os.getenv('RECAPTCHA_PUBLIC')
recaptcha_secret_key = os.getenv('RECAPTCHA_SECRET')

tinymce_api_key = os.getenv('TINYMCE_API')

