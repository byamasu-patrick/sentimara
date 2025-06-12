terraform {
  required_providers {
    digitalocean = {
      source = "digitalocean/digitalocean"
      version = "~> 2.0"
    }
  }
}

provider "digitalocean" {
    token = var.digitalocean_token
}

resource "digitalocean_droplet" "web" {
    image  = "ubuntu-24-04-x64"
    name   = "modellmind-ai"
    region = "nyc1"
    size   = "s-1vcpu-1gb"  
    ssh_keys = [var.ssh_fingerprint]
}


output "droplet_ip" {
    value = digitalocean_droplet.web.ipv4_address
}
