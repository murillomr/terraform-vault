import hvac
import os
from dotenv import load_dotenv
from pathlib import Path

# Carrega as variáveis do arquivo .env para o sistema
load_dotenv()

# Agora a obtenção dos valores de forma segura
VAULT_URL = os.getenv("VAULT_URL")
VAULT_TOKEN = os.getenv("VAULT_TOKEN")

load_dotenv(override=True) # O override força a substituição de qualquer valor padrão

def buscar_segredo_ia():
    try:
        client = hvac.Client(url=VAULT_URL, token=VAULT_TOKEN)
        
        # Ajustado conforme a sua GUI:
        # mount_point é o primeiro nome da rota (kv)
        # path é o nome do segredo (telegram)
        resposta = client.secrets.kv.v2.read_secret_version(
            path="telegram", 
            mount_point="kv"
        )
        
        # Pegando o valor da chave que você chamou de "telegram"
        token_telegram = resposta["data"]["data"]["telegram"]
        
        print("-" * 30)
        print(f"SUCESSO! Token do Telegram: {token_telegram}")
        print("-" * 30)

    except Exception as e:
        print(f"Erro ao ler o Vault: {e}")

if __name__ == "__main__":
    print("Entrou no bloco principal!")
    buscar_segredo_ia()
else:
    print("O script não reconheceu que está sendo executado diretamente.")