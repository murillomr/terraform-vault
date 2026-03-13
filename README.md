# 🛡️ AI Cloud-Native Lab: K3s + Terraform + Vault

Este repositório contém a infraestrutura como código (IaC) e os scripts de automação para provisionar um laboratório de Inteligência Artificial e Cybersecurity.

O ambiente é construído sobre um cluster K3s (Kubernetes) e utiliza o HashiCorp Vault para gestão centralizada e segura de segredos.

## 🚀 Arquitetura do Projeto

O objetivo é criar um ambiente robusto para o desenvolvimento de aplicações de IA, onde chaves de API (OpenAI, Anthropic, etc.) e outras credenciais nunca sejam expostas no código-fonte, seguindo as melhores práticas de DevSecOps.

-   **Cluster K3s:** Orquestração de contêineres leve, ideal para ambientes de laboratório rodando em MiniPCs ou VMs.
-   **HashiCorp Vault:** Gestão centralizada de segredos com persistência em disco. Provisionado via Helm.
-   **Terraform:** Automação do provisionamento da infraestrutura (Vault no K3s).
-   **Python (hvac):** Script de exemplo que demonstra a integração segura para consumo de credenciais em tempo de execução.

## 🛠️ Tecnologias Utilizadas

-   **OS:** Rocky Linux 10.1 (Blue Onyx) ou similar
-   **Orquestrador:** K3s v1.x
-   **IaC:** Terraform v1.x
-   **Secret Management:** HashiCorp Vault (Helm Chart)
-   **Linguagem:** Python 3.x com a biblioteca `hvac`

## ✅ Pré-requisitos

Antes de começar, garanta que você tenha as seguintes ferramentas instaladas e configuradas:

-   `kubectl` com acesso ao seu cluster Kubernetes.
-   `terraform` (v1.x ou superior).
-   `python` (3.6 ou superior) e `pip`.
-   Acesso a um cluster K3s ou outro Kubernetes.

## 📁 Estrutura do Projeto

```
.
├── .env.example    # Exemplo de como configurar as variáveis de ambiente
├── .gitignore      # Arquivos ignorados pelo Git
├── main.py         # Script Python para ler segredos do Vault
├── main.tf         # Arquivo principal do Terraform que provisiona o Vault
├── README.md       # Esta documentação
└── requirements.txt # Dependências do script Python
```

## 🔐 Implementação de Segurança

Este projeto implementa o **Princípio do Menor Privilégio**:

-   **Criptografia em Repouso:** O Vault armazena os dados de forma cifrada no disco.
-   **Unseal Protocol:** O cofre utiliza o algoritmo de Shamir. É necessário fornecer um quórum de chaves para liberar a chave mestra que decifra os dados.
-   **Separação de Camadas:** O Terraform gerencia a instalação, mas não armazena nem tem acesso às chaves de `unseal` ou aos tokens de autenticação, que são gerados dinamicamente e mantidos fora do controle de versão.

## 🚦 Guia de Instalação e Uso

Siga os passos abaixo para provisionar e configurar o ambiente.

### 1. Preparar o Ambiente K3s

Se ainda não tiver o K3s, instale-o em sua máquina Linux.

```bash
# Instalar o K3s
curl -sfL https://get.k3s.io | sh -

# Configurar permissões e variável de ambiente para o kubectl
sudo chown $USER /etc/rancher/k3s/k3s.yaml
export KUBECONFIG=/etc/rancher/k3s/k3s.yaml

# Verifique se o cluster está funcionando
kubectl get nodes
```
**Nota:** O comando `export` é válido apenas para a sessão atual do terminal. Para torná-lo permanente, adicione-o ao seu arquivo `~/.bashrc` ou `~/.zshrc`.

### 2. Instalar o Vault via Terraform

Com o cluster no ar, provisione o Vault.

```bash
# Navegue até a pasta do projeto
cd terraform-vault

# Inicialize o Terraform para baixar os providers
terraform init

# Revise o plano de execução
terraform plan

# Aplique a configuração para instalar o Vault
terraform apply --auto-approve
```

### 3. Inicializar e Abrir o Cofre (Unseal)

Esta é a etapa mais crítica, onde as chaves de segurança são geradas.

```bash
# Acesse o shell do pod do Vault
kubectl exec -n vault -it vault-0 -- /bin/sh

# Dentro do pod, execute os comandos do Vault:
# 1. Inicialize o Vault para gerar as chaves
vault operator init

# O comando acima retornará 5 chaves de unseal e 1 token raiz.
# GUARDE ESTAS INFORMAÇÕES EM LOCAL SEGURO! Elas não podem ser recuperadas.

# 2. Faça o "unseal" do Vault (repita 3 vezes com 3 chaves diferentes)
vault operator unseal <CHAVE_DE_UNSEAL_1>
vault operator unseal <CHAVE_DE_UNSEAL_2>
vault operator unseal <CHAVE_DE_UNSEAL_3>

# 3. Faça login com o token raiz gerado no passo de inicialização
vault login <SEU_TOKEN_RAIZ>
```

### 4. Configurar um Segredo de Exemplo

Vamos armazenar uma chave de API fictícia.

```bash
# (Ainda dentro do pod do Vault)

# Habilite o motor de segredos KV (Key-Value) versão 2
vault secrets enable -path=secret kv-v2

# Grave um segredo de exemplo
vault kv put secret/projeto-ia api_key="sk-12345abcdef"
```
Você pode sair do pod agora (`exit`).

### 5. Acessando a UI do Vault

O Vault foi exposto em um `NodePort`. Para acessá-lo:

1.  Descubra a porta alocada pelo Kubernetes:
    ```bash
    kubectl get service -n vault vault-ui -o=jsonpath='{.spec.ports[0].nodePort}'
    ```
2.  Acesse a UI em seu navegador: `http://<IP_DO_SEU_NÓ_K3S>:<PORTA_EXIBIDA_ACIMA>`
3.  Use o **Token Raiz** gerado anteriormente para fazer login.

### 6. Configurar e Rodar o Script Python

O script `main.py` lê o segredo que acabamos de criar.

1.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```
2.  **Crie o arquivo `.env`** com base no `.env.example`. Preencha com a URL do Vault e o Token Raiz.
    ```ini
    # .env
    VAULT_URL=http://<IP_DO_SEU_NÓ_K3S>:<PORTA_DO_SERVICE_VAULT>
    VAULT_TOKEN=<SEU_TOKEN_RAIZ>
    ```
    *   Para encontrar a porta do serviço do Vault (API, não UI), use: `kubectl get service -n vault vault -o=jsonpath='{.spec.ports[0].nodePort}'`.

3.  **Execute o script:**
    ```bash
    python main.py
    ```
    Se tudo estiver correto, o script imprimirá no console a `api_key` que você armazenou no Vault.

## 📝 Próximas Evoluções (Roadmap)

-   [ ] Implementar Vault Agent Injector para injeção automática de segredos via Sidecar.
-   [ ] Deploy de um modelo de linguagem local (Ollama) dentro do cluster.
-   [ ] Configuração de monitoramento com SIEM.
