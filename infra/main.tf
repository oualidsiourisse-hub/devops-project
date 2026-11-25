terraform {
  required_providers {
    kind = {
      source  = "tehcyx/kind"
      version = "0.13.0"
    }
  }
}

provider "kind" {}

resource "kind_cluster" "default" {
  name           = "devops-local"
  wait_for_ready = true

  kind_config {
    kind        = "Cluster"
    api_version = "kind.x-k8s.io/v1alpha4"

    node {
      role = "control-plane"

      extra_port_mappings {
        container_port = 30080
        host_port      = 8080
      }

      extra_port_mappings {
        container_port = 30090
        host_port      = 9090
      }
    }
  }
}