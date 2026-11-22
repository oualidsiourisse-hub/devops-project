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
}