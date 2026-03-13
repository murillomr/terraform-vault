# 1. Configuração dos Provedores
terraform {
  required_providers {
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.0"
    }
  }
}

provider "helm" {
  kubernetes {
    config_path = "/etc/rancher/k3s/k3s.yaml"
  }
}

# 2. Instalação do Vault via Helm
resource "helm_release" "vault" {
  name       = "vault"
  repository = "https://helm.releases.hashicorp.com"
  chart      = "vault"
  namespace  = "vault"
  create_namespace = true

  # Configurações customizadas do Vault
  values = [
    <<-EOT
    server:
      standalone:
        enabled: true
        config: |
          ui = true
          listener "tcp" {
            tls_disable = 1
            address     = "0.0.0.0:8200"
          }
          storage "file" {
            path = "/vault/data"
          }
      dataStorage:
        enabled: true
        size: 2Gi
      service:
        type: NodePort
      ui:
        enabled: true
        serviceType: NodePort
    EOT
  ]
}
