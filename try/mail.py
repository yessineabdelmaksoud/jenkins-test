import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- Paramètres SMTP ---
SMTP_SERVER = "smtp.gmail.com"   # Exemple : Gmail
SMTP_PORT = 587                  # Port TLS
EMAIL_SENDER = "yessineabdelmaksoud03@gmail.com"
EMAIL_PASSWORD = "xorakfzvxpcrscyf"  # Mot de passe d'application Gmail

# --- Destinataires ---
EMAIL_TO = ["yssineabdelmaksoud13@gmaail.com"]

# --- Contenu de l'email ---
subject = "Rapport Jenkins - Échec du Job"
body = """
Bonjour,

Le job Jenkins #42 a échoué.
Veuillez consulter les logs ici : http://jenkins.example.com/job/mon_job/42/console

Cordialement,
Agent LLM Jenkins
"""

# Création du message
message = MIMEMultipart()
message["From"] = EMAIL_SENDER
message["To"] = ", ".join(EMAIL_TO)
message["Subject"] = subject
message.attach(MIMEText(body, "plain"))

try:
    # Connexion au serveur SMTP
    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.starttls()  # Sécuriser la connexion
    server.login(EMAIL_SENDER, EMAIL_PASSWORD)

    # Envoi du mail
    server.sendmail(EMAIL_SENDER, EMAIL_TO, message.as_string())
    print("✅ Email envoyé avec succès !")

except Exception as e:
    print(f"❌ Erreur lors de l'envoi de l'email : {e}")

finally:
    server.quit()
