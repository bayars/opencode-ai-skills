---
name: nokia-netops
description: "Generate Nokia SR Linux and SR OS device configurations and Containerlab topologies by querying a ChromaDB knowledge base built from official Nokia documentation."
---

# Skill: Nokia NetOps

## Goal

Generate accurate Nokia SR Linux and SR OS (SROS) device configurations and Containerlab topology files by querying a ChromaDB vector database containing official Nokia documentation.

## Use This Skill When

- The user asks to configure Nokia SR Linux or SR OS devices
- The user wants to generate configs for cards, MDAs, interfaces, BGP, OSPF, MPLS, system settings
- The user asks to create a Containerlab topology with Nokia devices
- The user wants multi-device lab configs (e.g., "configure 5 SROS routers for BGP")

## Do Not Use This Skill When

- The user is asking about non-Nokia vendors (Cisco, Arista, Juniper)
- The user wants to interact with a live device API (use openapi-agent instead)
- The user is asking general networking theory without needing configs

## Inputs

- `platform` — `srlinux` or `sros` (or both)
- `task` — What to configure (natural language)
- `device_count` — Number of devices (default: 1)
- `topology` — Whether to generate a Containerlab topology (default: false)

## Knowledge Base

The ChromaDB knowledge base is populated by ingesting official Nokia documentation:

### SR Linux Sources
- Configuration Basics Guide (PDF/HTML)
- Interface Configuration Guide
- Network Instance Guide
- Routing Protocols Guide (BGP, OSPF, IS-IS)
- System Management Guide
- CLI Reference
- Source: `https://documentation.nokia.com/srlinux/`

### SR OS Sources
- Basic System Configuration Guide (PDF)
- Routing Protocols Guide (BGP, OSPF, IS-IS, MPLS)
- Services Guide (VPLS, VPRN, Epipe)
- MD-CLI User Guide
- CLI Reference
- Source: `https://documentation.nokia.com/html/0_add-h-f/93-0074-HTML/`

### ChromaDB Location
- Default: `./data/chromadb/`
- Collection: `nokia_docs`

## Steps

1. **Identify the platform** — SR Linux, SR OS, or both
2. **Query ChromaDB** for relevant configuration syntax and examples matching the user's task
3. **Determine device count and roles** — single device, spine-leaf, full mesh, hub-spoke
4. **Generate device configurations** following the correct CLI syntax:
   - SR Linux: structured `set` or tree-style config
   - SR OS: MD-CLI flat format or classic CLI
5. **Assign addressing** — loopbacks, point-to-point links, management IPs
6. **If topology requested**, generate a Containerlab `.clab.yml` file
7. **Output all configs** as separate files per device

## SR Linux Config Reference

### System / Hostname
```
system {
    name {
        host-name "leaf1"
    }
}
```

### Cards and Interfaces
```
interface ethernet-1/1 {
    admin-state enable
    subinterface 0 {
        ipv4 {
            admin-state enable
            address 10.0.0.1/30 {
            }
        }
    }
}
```

### BGP
```
network-instance default {
    interface ethernet-1/1.0 { }
    interface system0.0 { }
    protocols {
        bgp {
            admin-state enable
            autonomous-system 65001
            router-id 10.10.10.1
            group ebgp-peers {
                peer-as 65002
                ipv4-unicast {
                    admin-state enable
                }
            }
            neighbor 10.0.0.2 {
                peer-group ebgp-peers
            }
        }
    }
}
```

## SR OS Config Reference

### System Name
```
configure {
    system {
        name "router1"
    }
}
```

### Cards and MDAs
```
configure {
    card 1 {
        card-type iom-1
        mda 1 {
            mda-type me6-100gb-qsfp28
        }
    }
}
```

### Interfaces
```
configure {
    router "Base" {
        interface "to-router2" {
            port 1/1/1
            ipv4 {
                primary {
                    address 10.0.0.1
                    prefix-length 30
                }
            }
        }
        interface "system" {
            ipv4 {
                primary {
                    address 10.10.10.1
                    prefix-length 32
                }
            }
        }
    }
}
```

### BGP
```
configure {
    router "Base" {
        autonomous-system 65001
        router-id 10.10.10.1
        bgp {
            group "ebgp-peers" {
                peer-as 65002
            }
            neighbor 10.0.0.2 {
                group "ebgp-peers"
            }
        }
    }
}
```

## Containerlab Topology Reference

### SR Linux Topology
```yaml
name: srl-lab
topology:
  nodes:
    srl1:
      kind: nokia_srlinux
      type: ixr-d2l
      image: ghcr.io/nokia/srlinux
      startup-config: configs/srl1.cfg
    srl2:
      kind: nokia_srlinux
      type: ixr-d2l
      image: ghcr.io/nokia/srlinux
      startup-config: configs/srl2.cfg
  links:
    - endpoints: ["srl1:e1-1", "srl2:e1-1"]
```

### SR OS Topology
```yaml
name: sros-lab
topology:
  nodes:
    sros1:
      kind: nokia_sros
      type: sr-1
      image: vrnetlab/nokia_sros:23.10.R1
      license: license-sros.txt
      startup-config: configs/sros1.partial.cfg
    sros2:
      kind: nokia_sros
      type: sr-1
      image: vrnetlab/nokia_sros:23.10.R1
      license: license-sros.txt
      startup-config: configs/sros2.partial.cfg
  links:
    - endpoints: ["sros1:1/1/1", "sros2:1/1/1"]
```

### Mixed Topology
```yaml
name: mixed-lab
topology:
  kinds:
    nokia_srlinux:
      image: ghcr.io/nokia/srlinux
      type: ixr-d2l
    nokia_sros:
      image: vrnetlab/nokia_sros:23.10.R1
      type: sr-1
      license: license-sros.txt
  nodes:
    spine1:
      kind: nokia_sros
      startup-config: configs/spine1.partial.cfg
    leaf1:
      kind: nokia_srlinux
      startup-config: configs/leaf1.cfg
    leaf2:
      kind: nokia_srlinux
      startup-config: configs/leaf2.cfg
  links:
    - endpoints: ["spine1:1/1/1", "leaf1:e1-1"]
    - endpoints: ["spine1:1/1/2", "leaf2:e1-1"]
```

## Key Rules

- SR Linux interface naming: `ethernet-1/Y` (containerlab shorthand: `e1-Y`)
- SR OS interface naming: `1/1/X` (port on card 1, MDA 1)
- SR Linux default image: `ghcr.io/nokia/srlinux`
- SR OS image: `vrnetlab/nokia_sros:<version>` (requires license file)
- SR Linux default type: `ixr-d2l`
- SR OS default type: `sr-1`
- SR Linux credentials: `admin:NokiaSrl1!`
- SR OS credentials: `admin:admin`
- Always generate loopback/system interfaces for routing protocols
- Always assign unique router-id per device (use loopback IP)
- For BGP labs, assign unique ASN per device (eBGP) or same ASN (iBGP)

## Output

- One config file per device (named `<hostname>.cfg` or `<hostname>.partial.cfg`)
- One `topology.clab.yml` file if topology is requested
- A summary table: device name, role, loopback IP, ASN, connections
