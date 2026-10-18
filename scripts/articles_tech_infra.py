# -*- coding: utf-8 -*-
"""
Deep Technical Post-Mortems and Architecture Reports: Infrastructure, Storage, & Networking.
All articles written in English with A4-report depth.
"""

ARTICLES_TECH_INFRA = {
    "cascading-failure-network-time-etcd-storage": {
        "title": "Post-Mortem: A 4-Stage Cascading Failure Across Network, Time Drift, Etcd, and Longhorn Storage",
        "excerpt": "An exhaustive post-mortem of a production outage triggered by an MTU mismatch on overlay interfaces, which cascaded into NTP clock desynchronization, etcd cluster quorum loss, and ultimately caused Longhorn iSCSI storage targets to remount as read-only across all worker nodes.",
        "markdown": """## 1. Executive Summary & Incident Timeline

During a scheduled network re-architecture of our bare-metal Kubernetes (k3s) cluster, a subtle Maximum Transmission Unit (MTU) mismatch on the physical uplink interfaces triggered a catastrophic four-stage cascading failure. Over a 90-minute window, what appeared to be isolated packet drops evolved into clock synchronization failure, etcd quorum loss, and mass iSCSI disconnection of Longhorn distributed block volumes, causing stateful databases and web services to crash with read-only filesystem errors.

- **Severity**: SEV-1 (Total cluster stateful workload outage)
- **Time to Detect (TTD)**: 4 minutes
- **Time to Remediate (TTR)**: 86 minutes
- **Root Cause**: An upstream switch port MTU change dropped jumbo UDP packets, causing chrony NTP peers to time out. Cumulative clock skew exceeded 120 seconds, breaking Raft consensus in etcd and triggering unrecoverable iSCSI SCSI session resets on Longhorn storage replicas.

```
[Physical MTU Drop] ──> [NTP UDP Fragmentation] ──> [120s Clock Drift]
                                                           │
[Storage Read-Only] <── [Longhorn iSCSI Reset] <── [Etcd Quorum Loss]
```

---

## 2. Anatomy of the 4-Stage Cascading Failure

### Stage 1: The Silent Packet Drop (MTU Blackhole)
The cluster nodes communicate over 10Gbps physical links connected through a top-of-rack switch. A configuration sync on the physical switch reset port MTUs from 9000 bytes down to 1500 bytes. While standard TCP traffic performed Path MTU Discovery (PMTUD) and negotiated smaller MSS (Maximum Segment Size), stateless UDP packets exceeding 1500 bytes—specifically large NTP sync packets with cryptographic authentication tags and Geneve/VXLAN overlay encapsulation—were silently dropped without ICMP Fragmentation Needed (Type 3, Code 4) notifications.

### Stage 2: Time Drift & Asymmetric Clock Skew
Because chrony was configured with an internal NTP pool that exchanged extended telemetry frames, NTP query-response cycles failed. Within 45 minutes, node clocks diverged by more than 120,000 milliseconds (120 seconds) due to hardware oscillator frequency drift under variable CPU load.
```bash
# chronyc tracking on affected worker node
Reference ID    : 00000000 ()
Stratum         : 0
Ref time (UTC)  : Thu Jan 01 00:00:00 1970
System time     : 124.812391021 seconds slow of NTP time
Last offset     : +0.000000000 seconds
RMS offset      : 0.000000000 seconds
Frequency       : 24.120 ppm slow
Leap status     : Not synchronised
```

### Stage 3: Raft Heartbeat Timeout and Etcd Quorum Loss
Etcd relies on monotonic time for leader election and lease revocation. When clock drift across etcd members exceeded the election timeout (`election-timeout = 1000ms`), node members concluded that their peers had died. Raft election storms erupted:
```log
etcdserver: failed to send out heartbeat on time (exceeded the 100ms timeout for 1420ms)
raft: 8a712f2c8d failed to send message to 4e21a8b9e: connection reset by peer
etcdserver: lost leader 8a712f2c8d, starting new election at term 412
etcdserver: publish error: etcdserver: request timed out
```
The Kubernetes API server lost its backing datastore, entering an unresponsive state and failing admission webhooks.

### Stage 4: Longhorn iSCSI Death Spiral & Read-Only Remounts
Longhorn uses an iSCSI target daemon (`tgt`) to expose block devices to host nodes. When the control plane collapsed and etcd leases expired, the Longhorn instance manager could not renew its heartbeat leases. Concurrently, kernel iSCSI initiators (`iscsid`) detected timeout anomalies across the network.
```log
kernel: [ 4512.890123] connection1:0: ping timeout of 5 secs expired, recv timeout 5, last rx 4507890, last ping 4512890, now 4517890
kernel: [ 4512.890145] connection1:0: detected conn error (1022)
kernel: [ 4517.912340] sd 4:0:0:1: [sdd] aborting command 0x2a
kernel: [ 4522.956789] sd 4:0:0:1: [sdd] tag#12 FAILED Result: hostbyte=DID_TIME_OUT
kernel: [ 4522.956812] EXT4-fs error (device sdd): ext4_lookup: deleted inode referenced: 1310722
kernel: [ 4522.956834] Aborting journal on device sdd-8.
kernel: [ 4522.989012] EXT4-fs (sdd): Remounting filesystem read-only
```
Critical database pods (PostgreSQL, OpenSearch, MinIO) crashed immediately upon attempting filesystem write operations.

---

## 3. Emergency Remediation & Recovery Runbook

### Step 1: Clamp Interface MTU
Immediately force all physical and virtual interfaces down to a safe MTU baseline of 1420 (allowing for Cilium Geneve overlay encapsulation overhead):
```bash
# On all physical hosts
sudo ip link set dev eth0 mtu 1500
sudo ip link set dev cilium_vxlan mtu 1420

# Verify PMTU using ping with Don't Fragment (DF) flag
ping -c 3 -M do -s 1472 192.168.10.1
```

### Step 2: Step-Force Clock Synchronization
Restart and step the system clock immediately across all cluster nodes:
```bash
sudo systemctl stop chrony
sudo chronyd -q 'server pool.ntp.org iburst'
sudo systemctl start chrony
chronyc tracking
```

### Step 3: Recover Etcd Quorum
Once node clocks were synchronized within 2ms, etcd leader elections stabilized automatically. For stubborn nodes with corrupted WAL entries:
```bash
# Verify member health
etcdctl endpoint health --cluster -w table
etcdctl endpoint status --cluster -w table
```

### Step 4: Revive Longhorn Volumes and Repair Filesystems
With etcd operational, Longhorn volume targets had to be cleanly detached, verified via `fsck`, and reattached to application pods:
```bash
# Scale down stateful workloads
kubectl scale deployment/blog-emdash -n blog-stg --replicas=0
kubectl scale statefulset/blog-db-postgresql -n blog-stg --replicas=0

# Execute filesystem consistency check on the underlying host volume
sudo fsck.ext4 -y /dev/longhorn/pvc-49a71b82-9901-4c1d-8b01-fb7890123456

# Scale workloads back up
kubectl scale statefulset/blog-db-postgresql -n blog-stg --replicas=1
kubectl scale deployment/blog-emdash -n blog-stg --replicas=1
```

---

## 4. Permanent Architectural Hardening Measures

1. **Strict MTU Clamping in CNI**: Set `cilium.mtu: 1420` explicitly in the Helm chart values, preventing dynamic MTU calculation errors during uplink state transitions.
2. **Prometheus Clock Drift Alerting**: Deployed Node Exporter with alerts triggering if `node_timex_offset_seconds > 0.05` (50ms skew).
3. **iSCSI Initiator Timeout Tuning**: Tuned `/etc/iscsi/iscsid.conf` to avoid premature SCSI resets:
   ```ini
   node.session.timeo.replacement_timeout = 60
   node.conn[0].timeo.noop_out_interval = 5
   node.conn[0].timeo.noop_out_timeout = 10
   ```
4. **Etcd Tuning for Bare-Metal Workloads**: Increased heartbeat interval to 250ms and election timeout to 1250ms in k3s server configuration flags to tolerate brief network micro-bursts.
"""
    },

    "cilium-tailscale-routing-loop-mtu-investigation": {
        "title": "Debugging Linux Kernel Routing Loops: Cilium eBPF Host-Routing, Tailscale WireGuard, and 1000ms Latency",
        "excerpt": "A rigorous deep dive into an elusive networking bug where Kubernetes Pods communicating with Tailscale exit nodes suffered 1,000ms ping spikes and packet drops due to Cilium eBPF host-routing bypassing iptables marks and creating packet loops.",
        "markdown": """## 1. Problem Statement & Symptoms

In our hybrid cloud infrastructure, Kubernetes pods require secure outbound access to private cloud resources and exit nodes over a Tailscale WireGuard mesh network. While host-level network traffic to Tailscale IPs (`100.64.0.0/10`) was lightning fast (< 12ms RTT), pods running on the same host experienced catastrophic network degradation:
- Ping round-trip times (RTT) consistently exceeded **1,000ms** to **1,200ms**.
- TCP connections suffered massive SYN retransmissions and dropped after 30 seconds.
- Curl requests to remote endpoints produced sporadic `HTTP 504 Gateway Timeout` or `Recv failure: Connection reset by peer`.

---

## 2. Kernel Packet Tracing with eBPF

To diagnose where packets were disappearing or getting delayed, we deployed low-level tracing tools across the network stack.

```
Pod (eth0) ──> [Cilium eBPF tc egress] ──> [Bypasses iptables fwmark!]
                     ▲                                │
                     │                       [Physical eth0]
                     │                                │
                     └── [Loopback to tailscale0] <───┘
```

### Inspecting Cilium Drops
Running `cilium monitor` on the affected node revealed continuous packet redirects and drop events:
```bash
cilium monitor --type drop -v
# Output:
xx drop (FibLookupFailed) flow 0x9a8f211 to ifindex 0 from cnx 10.42.1.85:41234 -> 100.80.25.10:443, reason: Fib lookup failed
xx drop (HopLimitExceeded) flow 0x9a8f211 to ifindex 4 from cnx 10.42.1.85:41234 -> 100.80.25.10:443, reason: TTL expired in transit
```

Notice the critical indicator: `HopLimitExceeded` (TTL expired in transit). This proved beyond doubt that a packet routing loop was occurring entirely within the Linux kernel network stack of a single physical node!

---

## 3. Unveiling the Root Cause

The routing loop was created by the collision of two advanced networking mechanisms:

1. **Tailscale Policy Routing**:
   Tailscale uses Linux policy routing rules and iptables firewall marks (`fwmark 0x80000`). Outgoing packets destined for the Tailscale CGNAT subnet (`100.64.0.0/10`) must be marked so they hit routing table `52` and enter the `tailscale0` WireGuard tun device.
2. **Cilium eBPF Host Routing (`bpf-routing: true`)**:
   By default, modern Cilium installations use eBPF programs attached to the Traffic Control (`tc`) hooks of the physical interface (`eth0`) and pod veth interfaces. To achieve maximum throughput, Cilium's BPF programs perform direct FIB (Forwarding Information Base) lookups in eBPF and transmit packets directly via `bpf_redirect_neigh()`, **completely bypassing the Linux netfilter/iptables stack**.

Because Cilium bypassed netfilter:
1. Pod egress packets were never marked with `fwmark 0x80000`.
2. The packet reached the physical `eth0` interface instead of `tailscale0`.
3. The host routing table re-evaluated the packet destination, sent it back to `tailscale0`.
4. `tailscale0` encapsulated the packet, but Cilium's ingress BPF hook intercepted it again.
5. The packet looped 64 times until its IPv4 TTL decremented to 0, burning CPU cycles and ballooning latency to over 1,000ms.

---

## 4. The Architectural Solution

To eliminate the collision, we tuned Cilium's host routing architecture to respect Linux network namespace boundaries and policy routing tables.

### Step 1: Enable Host Legacy Routing in Cilium
We updated the Cilium Helm values to enable `host-legacy-routing`:
```yaml
# cilium-values.yaml
routingMode: tunnel
tunnelProtocol: vxlan
bpf:
  hostLegacyRouting: true
  masquerade: true
```
This forces packets leaving pod namespaces into host network namespaces to transit through the standard Linux network stack, allowing netfilter hooks and `fwmark` rules to evaluate normally.

### Step 2: Configure Route Rules for Pod Subnets
We added explicit policy routing rules ensuring pod IP CIDRs route through table 52 when targeting the Tailscale network:
```bash
# Add routing rule for Cilium pod subnet (e.g., 10.42.0.0/16)
sudo ip rule add from 10.42.0.0/16 to 100.64.0.0/10 lookup 52 pref 5150
```

### Step 3: MTU Clamping on WireGuard & Overlay
Because WireGuard adds 80 bytes of encapsulation overhead and Cilium adds 50 bytes of Geneve/VXLAN headers:
- Physical interface MTU: 1500
- Tailscale `tailscale0` MTU: 1280
- Cilium Pod MTU: Explicitly set to 1280 to prevent TCP MSS truncation issues.

---

## 5. Verification & Performance Benchmarking

Following the fix, we benchmarked pod-to-Tailscale network performance under sustained load:

```bash
# Test from inside a Kubernetes pod
kubectl run net-test --rm -it --image=curlimages/curl -- curl -o /dev/null -s -w 'Total Time: %{time_total}s, HTTP: %{http_code}\n' https://internal-exit.node.tailscale/healthz
# Total Time: 0.012140s, HTTP: 200

# Ping verification
kubectl run ping-test --rm -it --image=busybox -- ping -c 10 100.80.25.10
# 10 packets transmitted, 10 packets received, 0% packet loss
# round-trip min/avg/max = 11.2/12.4/13.8 ms
```

Latency dropped by **98.8%** (from 1,040ms down to 12.4ms), and packet loss dropped to exactly 0%.
"""
    },

    "traefik-v3-cross-namespace-404-resolution": {
        "title": "Traefik v3 IngressRoute Cross-Namespace Routing: Resolving 404 Not Found and Provider Configuration Gotchas",
        "excerpt": "Demystifying Traefik v3's security boundaries for cross-namespace routing: why multi-namespace microservices throw 404 errors with IngressRoute and how to properly configure providers and RBAC.",
        "markdown": """## 1. Multi-Namespace Topologies in Modern Kubernetes

In modern Kubernetes cluster design, strict namespace isolation is the primary boundary for security and tenancy. A standard enterprise topology places the gateway infrastructure in a dedicated namespace (e.g., `traefik`), while business applications and API services reside in isolated application namespaces (e.g., `blog-stg`, `auth`, `monitoring`).

With Traefik's Custom Resource Definition (`IngressRoute`), platform engineers frequently define an ingress router in one namespace that references backend Kubernetes services in another namespace:

```yaml
# IngressRoute in 'traefik' or application namespace referencing cross-namespace service
apiVersion: traefik.io/v1alpha1
kind: IngressRoute
metadata:
  name: platform-dashboard
  namespace: traefik
spec:
  entryPoints:
    - websecure
  routes:
    - match: Host(`dashboard.lab.internal`)
      kind: Rule
      services:
        - name: monitoring-grafana
          namespace: monitoring
          port: 80
```

However, deploying this manifest in Traefik v3 immediately produces an infuriating symptom: **HTTP 404 Not Found** on all incoming requests, with no obvious error in the application logs.

---

## 2. Root Cause: Traefik v3's Zero-Trust Default Security Boundary

Unlike Traefik v2 where cross-namespace references were often permissive depending on provider defaults, **Traefik v3 enforces strict namespace encapsulation out-of-the-box**. 

To mitigate multi-tenant spoofing attacks (where a malicious tenant in namespace A defines an IngressRoute that hijacks traffic intended for namespace B's internal services), Traefik v3 silently drops any cross-namespace service or middleware reference unless two mandatory prerequisites are met:

1. The Kubernetes CRD provider has explicit cross-namespace permission enabled via command-line flags.
2. The Traefik Controller's ServiceAccount possesses cluster-wide RBAC permissions to inspect endpoints and services across all referenced namespaces.

If either condition is missing, Traefik's internal configuration engine marks the child router as invalid and refuses to bind it to the entryPoint, resulting in an immediate 404.

---

## 3. Step-by-Step Resolution Runbook

### Step 1: Enable `allowCrossNamespace` on the CRD Provider
If managing Traefik via Helm, update `values.yaml` to include the following configuration:

```yaml
# traefik-values.yaml
providers:
  kubernetesCRD:
    enabled: true
    allowCrossNamespace: true
  kubernetesIngress:
    enabled: true
    allowCrossNamespace: true
```

If passing CLI arguments directly to the Traefik deployment container:
```bash
--providers.kubernetescrd.allowCrossNamespace=true
--providers.kubernetesingress.allowCrossNamespace=true
```

### Step 2: Verify and Update ClusterRole RBAC
When `allowCrossNamespace` is enabled, Traefik must have cluster-scoped permissions. Verify that Traefik is bound to a `ClusterRole` (not a namespace-scoped `Role`):

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: traefik-ingress-controller
rules:
  - apiGroups: [""]
    resources: ["services", "endpoints", "secrets"]
    verbs: ["get", "list", "watch"]
  - apiGroups: ["traefik.io"]
    resources:
      - ingressroutes
      - ingressroutetcps
      - ingressrouteudps
      - middlewares
      - middlewaretcps
      - tlsoptions
      - tlsstores
      - traefikservices
      - serverstransports
    verbs: ["get", "list", "watch"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: traefik-ingress-controller
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: traefik-ingress-controller
subjects:
  - kind: ServiceAccount
    name: traefik
    namespace: traefik
```

---

## 4. Cross-Namespace Middleware References

A secondary trap in Traefik v3 involves Middleware definitions. When referencing a common security middleware (such as Coraza WAF or CrowdSec bouncer) defined in the `traefik` namespace from an `IngressRoute` in the `blog-stg` namespace:

```yaml
# IngressRoute in namespace 'blog-stg'
apiVersion: traefik.io/v1alpha1
kind: IngressRoute
metadata:
  name: blog-emdash
  namespace: blog-stg
spec:
  entryPoints: [websecure]
  routes:
    - match: Host(`blog-stg.lab.internal`)
      kind: Rule
      middlewares:
        # Syntax: <middleware-name>@kubernetescrd OR <namespace>-<middleware-name>@kubernetescrd
        - name: traefik-coraza-waf
          namespace: traefik
      services:
        - name: blog-emdash
          port: 4321
```

Notice that both `name` and `namespace` must be explicitly declared, and `allowCrossNamespace: true` must be active for middlewares as well as services.

---

## 5. Verification Checklist

1. **Check Traefik Controller Logs**:
   ```bash
   kubectl logs -n traefik deployment/traefik | grep -E "level=(warning|error)"
   ```
   Ensure there are no `skipping cross-namespace service` or `cannot create service: cross-namespace references are not allowed` messages.
2. **Inspect Traefik API Dashboard**:
   Port-forward to the internal dashboard and verify that the router is listed with a green status under HTTP Routers.
3. **Curl Ingress Endpoint**:
   ```bash
   curl -I https://blog-stg.lab.internal/
   # HTTP/2 200 OK
   ```
"""
    },

    "internal-ca-injection-trust-manager-kyverno-pivot": {
        "title": "Zero-Trust PKI in Kubernetes: Why We Abandoned Kyverno for Cert-Manager Trust-Manager for Root CA Distribution",
        "excerpt": "An architectural review of distributing internal step-ca and Let's Encrypt private certificates across dozens of Kubernetes namespaces, explaining why dynamic Kyverno mutation policies failed and how cert-manager trust-manager delivered rock-solid reliability.",
        "markdown": """## 1. The Challenge of Enterprise Internal PKI

In a zero-trust Kubernetes environment, applications do not simply accept arbitrary public certificates. Internal microservices communicate over mutual TLS (mTLS) anchored by an internal Root Certificate Authority (Step-CA or HashiCorp Vault), while private container registries, GitOps webhooks, and observability agents require validated TLS connections with custom CA bundles.

To enable Linux containers (using OpenSSL, curl, Go crypto, or Java JVM truststores) to validate these internal certificates, the enterprise Root CA bundle must be made available inside every container at standard system paths:
- Debian/Ubuntu: `/etc/ssl/certs/ca-certificates.crt`
- Alpine Linux: `/etc/ssl/certs/ca-certificates.crt`
- RedHat/CentOS: `/etc/pki/tls/certs/ca-bundle.crt`

Distributing and keeping this CA bundle synchronized across 20+ dynamic namespaces is a critical operational problem.

---

## 2. The First Attempt: Kyverno Mutate & Generate Policies

Initially, we implemented CA injection using **Kyverno**, the popular Kubernetes-native policy engine. We created a `ClusterPolicy` that:
1. Watched for new namespace creation and automatically generated a `ConfigMap` containing the internal Root CA.
2. Intercepted all Pod creation requests via a Mutating Admission Webhook to automatically inject a `volume` and `volumeMount` pointing to `/etc/ssl/certs/ca-certificates.crt`.

```yaml
# The Legacy Kyverno Mutate Rule (Fragile)
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: inject-internal-ca
spec:
  rules:
    - name: mutate-pod-ca-mount
      match:
        resources:
          kinds: ["Pod"]
      mutate:
        patchStrategicMerge:
          spec:
            volumes:
              - name: trusted-ca-volume
                configMap:
                  name: enterprise-root-ca
            containers:
              - name: "*"
                volumeMounts:
                  - name: trusted-ca-volume
                    mountPath: /etc/ssl/certs/ca-certificates.crt
                    subPath: ca-certificates.crt
```

### Why Kyverno Broke in Production
While functional on paper, this architecture caused severe production incidents:
1. **Admission Webhook Timeouts**: When the cluster was under heavy load or during node reboots, Kyverno's webhook latency caused kubelet pod creation to exceed timeouts, leaving pods in `CreateContainerError`.
2. **Race Condition on Namespace Creation**: When GitOps (ArgoCD) deployed a new namespace simultaneously with application manifests, the Pod mutation rule evaluated before the Kyverno Generate rule had finished creating the `ConfigMap`, resulting in `MountVolume.SetUp failed for volume "trusted-ca-volume" : configmap "enterprise-root-ca" not found`.
3. **SubPath Volume Mount Incompatibilities**: Using `subPath` prevented dynamic CA rotation; when the CA changed, mounted files inside running pods remained stale until pods were forcefully restarted.

---

## 3. The Architectural Pivot: Cert-Manager `trust-manager`

To eliminate admission webhook risks and ensure reliable synchronization, we migrated to **cert-manager `trust-manager`**.

```
[cert-manager] ──> [Root CA Secret] ──> [trust-manager Bundle]
                                                │
                 ┌──────────────────────────────┴──────────────────────────────┐
                 ▼                                                             ▼
    [Namespace: blog-stg]                                             [Namespace: ai]
ConfigMap: enterprise-ca-bundle                                ConfigMap: enterprise-ca-bundle
```

`trust-manager` is an operator designed exclusively for one purpose: aggregating trust bundles and projecting them into `ConfigMaps` across all cluster namespaces using a lightweight controller reconciler—without relying on mutating admission webhooks.

### Key Advantages of trust-manager:
- **No Admission Webhook Overhead**: Operates entirely asynchronously via controller reconciliation loops.
- **Bundle Aggregation**: Can automatically combine a public CA bundle (e.g., default Mozilla root certificates) with internal private CAs into a unified single pem file.
- **Immediate Propagation**: Changes to the root CA secret are synced to all namespaces within seconds.

---

## 4. Production Implementation Guide

### Step 1: Deploy trust-manager via Helm
```bash
helm repo add jetstack https://charts.jetstack.io
helm repo update

helm upgrade --install trust-manager jetstack/trust-manager \
  --namespace cert-manager \
  --set defaultPackage.enabled=true \
  --wait
```

### Step 2: Define the Unified Cluster Bundle
Create the `Bundle` custom resource that combines the default Mozilla public certificates with our internal step-ca Root CA:

```yaml
apiVersion: trust.cert-manager.io/v1alpha1
kind: Bundle
metadata:
  name: enterprise-trusted-ca
spec:
  sources:
    # 1. Include default Mozilla public trusted root certificates
    - useDefaultCAs: true
    # 2. Include internal enterprise Root CA from cert-manager Secret
    - secret:
        name: internal-step-ca-root-cert
        key: "root-ca.crt"
  target:
    configMap:
      key: "ca-certificates.crt"
    # Target all namespaces automatically
    namespaceSelector: {}
```

Once applied, `trust-manager` instantly provisions a `ConfigMap` named `enterprise-trusted-ca` in every existing and newly created namespace containing the complete, valid certificate bundle.

---

## 5. Verification and Mount Best Practices

For workloads requiring custom CA trust, mount the generated ConfigMap cleanly:

```yaml
spec:
  containers:
    - name: app
      image: my-service:latest
      volumeMounts:
        - name: ca-bundle
          mountPath: /etc/ssl/certs
          readOnly: true
  volumes:
    - name: ca-bundle
      configMap:
        name: enterprise-trusted-ca
        items:
          - key: ca-certificates.crt
            path: ca-certificates.crt
```

### Validation Test
```bash
# Execute inside any pod in the cluster
kubectl exec -it deployment/blog-emdash -n blog-stg -- curl -v https://auth.lab.internal/healthz
# Output:
# * SSL connection using TLSv1.3 / TLS_AES_256_GCM_SHA384
# * Server certificate:
# *  subject: CN=auth.lab.internal
# *  issuer: CN=Internal Step CA Root
# * SSL certificate verify ok.
# < HTTP/2 200
```
"""
    },

    "kubevirt-multus-l2-policy-routing": {
        "title": "KubeVirt Dual-Stack Multus L2 Networking: Linux Policy Routing (ip rule pref 5200) and Bridge CNI Isolation",
        "excerpt": "Configuring high-performance dual-NIC virtual machines in KubeVirt with direct Layer 2 network attachment, overcoming asymmetric routing and default gateway conflicts with Linux policy routing.",
        "markdown": """## 1. The Challenge of Dual-Homed Virtual Machines in Kubernetes

When running virtualized research environments (such as CTI honeypots, malware analysis sandboxes, or Whonix gateway workstations) alongside containerized microservices in KubeVirt, virtual machines frequently require dual network interfaces:
1. **Primary Interface (`eth0`)**: The standard Kubernetes pod network (managed by Cilium/Calico) for cluster DNS, Prometheus metrics scraping, and management access via `virtctl`.
2. **Secondary Interface (`eth1`)**: A direct Layer-2 bridge or macvlan attachment to a physical VLAN, providing direct WAN connectivity, Tor routing, or packet capture without NAT translation.

However, attaching a second L2 interface introduces a notorious networking pathology: **Asymmetric Routing and Default Gateway Collision**.

---

## 2. Anatomy of the Asymmetric Routing Trap

```
[External Client] ──(SYN)──> [Physical VLAN] ──> [VM eth1: 192.168.20.50]
                                                           │
[External Client] <──(SYN-ACK Dropped!) <── [Pod Gateway: 10.42.0.1 (eth0)]
```

When an external client sends a TCP SYN packet to the VM's secondary IP address (`192.168.20.50` on `eth1`), the Linux kernel inside the guest VM accepts the packet. However, when generating the TCP SYN-ACK response:
1. The kernel consults its routing table.
2. Because the system has only one default gateway (`default via 10.42.0.1 dev eth0`), the reply packet is routed out through `eth0`.
3. The upstream firewall or router observes a SYN-ACK originating from an unexpected IP or interface, detects a state violation, and drops the connection with `RST` or silent timeout.

---

## 3. The Solution: Linux Policy-Based Routing (`ip rule pref 5200`)

To ensure that traffic arriving on the secondary interface is always answered through that same interface regardless of the destination IP, we implement source-based policy routing.

### Step 1: Create an Isolated Routing Table
We define a dedicated routing table (`table 100`) for the secondary L2 interface:
```bash
# Define table 100 with default route via the L2 gateway
ip route add 192.168.20.0/24 dev eth1 proto kernel scope link src 192.168.20.50 table 100
ip route add default via 192.168.20.1 dev eth1 table 100
```

### Step 2: Add Policy Routing Rule with Explicit Priority
We bind traffic originating from the secondary IP to table 100 using `ip rule` with a high preference priority:
```bash
# Route all packets from 192.168.20.50 using table 100
ip rule add from 192.168.20.50/32 lookup 100 pref 5200
```

By assigning preference `5200`, this rule evaluates before the default routing rules (`pref 32766`), guaranteeing deterministic return-path routing!

---

## 4. Declarative Cloud-Init Configuration

To automate this setup across VM restarts and dynamic provisioning, we embed the policy routing logic directly into the KubeVirt `VirtualMachine` manifest via Cloud-Init (Netplan):

```yaml
apiVersion: kubevirt.io/v1
kind: VirtualMachine
metadata:
  name: research-worker-vm
  namespace: security-research
spec:
  running: true
  template:
    spec:
      domain:
        devices:
          interfaces:
            # Primary Pod Network
            - name: default
              masquerade: {}
            # Secondary L2 Bridge Network
            - name: vlan-l2
              bridge: {}
      networks:
        - name: default
          pod: {}
        - name: vlan-l2
          multus:
            networkName: l2-bridge-conf
      volumes:
        - name: cloudinit
          cloudInitNoCloud:
            userData: |
              #cloud-config
              write_files:
                - path: /etc/netplan/60-secondary-l2.yaml
                  content: |
                    network:
                      version: 2
                      ethernets:
                        eth1:
                          dhcp4: false
                          addresses:
                            - 192.168.20.50/24
                          routes:
                            - to: default
                              via: 192.168.20.1
                              table: 100
                          routing-policy:
                            - from: 192.168.20.50
                              table: 100
                              priority: 5200
              runcmd:
                - netplan apply
```

---

## 5. NetworkAttachmentDefinition (Bridge CNI)

Ensure the Multus `NetworkAttachmentDefinition` is configured on the host cluster:
```yaml
apiVersion: "k8s.cni.cncf.io/v1"
kind: NetworkAttachmentDefinition
metadata:
  name: l2-bridge-conf
  namespace: security-research
spec:
  config: '{
    "cniVersion": "0.3.1",
    "name": "l2-bridge",
    "type": "bridge",
    "bridge": "br-vlan20",
    "isGateway": false,
    "ipam": {}
  }'
```

---

## 6. Verification and Throughput Testing

From an external client on VLAN 20:
```bash
# TCP Ping and Curl Test
curl -I http://192.168.20.50/
# HTTP/1.1 200 OK

# Iperf3 Line-Rate Benchmark
iperf3 -c 192.168.20.50 -t 10
# [ ID] Interval           Transfer     Bitrate         Retr
# [  5]   0.00-10.00  sec  11.4 GBytes  9.78 Gbits/sec    0    sender
# [  5]   0.00-10.00  sec  11.4 GBytes  9.75 Gbits/sec         receiver
```
Full 10Gbps line-rate throughput achieved with zero packet loss and zero asymmetric routing drops.
"""
    },

    "kubevirt-storage-tuning-block-datavolume-longhorn": {
        "title": "KubeVirt VM Storage Performance Optimization: Filesystem vs RAW Block DataVolumes on Longhorn Distributed Block Storage",
        "excerpt": "Benchmarking and optimizing virtual machine disk I/O in KubeVirt: why switching from filesystem-backed qcow2 images to RAW block volumeMode on Longhorn delivered a 400% boost in random 4K IOPS.",
        "markdown": """## 1. Storage in KubeVirt: The Double-Filesystem Penalty

Running production virtual machines inside Kubernetes requires resilient, replicated persistent storage. Longhorn is widely chosen for bare-metal Kubernetes due to its ease of deployment, snapshot capabilities, and distributed data replication.

However, default KubeVirt quickstart tutorials typically recommend creating virtual disks inside standard PVCs with `volumeMode: Filesystem`. This innocent default introduces a crippling architectural flaw known as the **Double-Filesystem and Double-Journaling Penalty**:

```
[Guest VM OS (ext4)]
         │
[QEMU qcow2 Image File]
         │
[Host Kubernetes PVC Mount (ext4)]  <── Double journaling & lock contention!
         │
[Longhorn iSCSI Engine & Block Replicas]
```

When an application inside the VM writes a block of data:
1. The guest filesystem logs the change to its journal and writes to the virtual disk.
2. The QEMU disk emulator translates the write into POSIX write calls targeting a `.qcow2` file.
3. The host filesystem (`ext4` on the Longhorn block device) logs the write to its own journal.
4. Longhorn's iSCSI target synchronously replicates the physical block across cluster nodes.

The result is severe I/O amplification, latency spikes, and CPU starvation in the `virt-launcher` pod.

---

## 2. FIO Benchmark: The Baseline Filesystem Penalty

To quantify this overhead, we ran standardized Flexible I/O Tester (`fio`) benchmarks inside a Debian 12 KubeVirt VM configured with standard filesystem-backed storage:

```ini
# fio benchmark profile: random 4k read/write
[global]
ioengine=libaio
direct=1
runtime=60
time_based
size=4G
filename=/mnt/test/fio.test

[rand-write-4k]
bs=4k
iodepth=32
rw=randwrite
```

### Baseline Performance (volumeMode: Filesystem):
- **Random 4K Write IOPS**: **1,820 IOPS**
- **Average Write Latency**: **17.5 ms**
- **99th Percentile (p99) Latency**: **48.2 ms**
- **Virt-Launcher CPU Utilization**: High (280% vCPU during benchmark)

---

## 3. The Architectural Shift: RAW Block VolumeMode

To eliminate the translation layer, we migrated the virtual disk architecture to `volumeMode: Block`.

```
[Guest VM OS (ext4 / XFS)]
         │
[Direct Block Device Passthrough (/dev/longhorn/pvc-...)]
         │
[Longhorn iSCSI Engine & Block Replicas]
```

With `volumeMode: Block`:
- No host filesystem is formatted.
- The Longhorn block device is passed directly into the KVM/QEMU hypervisor as a raw block target (`virtio-blk`).
- The guest VM reads and writes directly to raw blocks, eliminating host filesystem journaling and lock contention entirely.

---

## 4. Implementation Guide: Deploying Block DataVolumes

### Step 1: Longhorn StorageClass for Block Devices
Create a dedicated StorageClass for KubeVirt block volumes:
```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: longhorn-kubevirt-block
provisioner: driver.longhorn.io
allowVolumeExpansion: true
reclaimPolicy: Delete
volumeBindingMode: Immediate
parameters:
  numberOfReplicas: "2"
  staleReplicaTimeout: "2880"
  dataLocality: "best-effort"
```

### Step 2: Define VirtualMachine with Block DataVolume
```yaml
apiVersion: kubevirt.io/v1
kind: VirtualMachine
metadata:
  name: cti-collector-vm
  namespace: security-research
spec:
  running: true
  template:
    spec:
      domain:
        devices:
          disks:
            - name: rootdisk
              disk:
                bus: virtio
        resources:
          requests:
            memory: 4Gi
            cpu: 2000m
      volumes:
        - name: rootdisk
          dataVolume:
            name: cti-collector-disk
  dataVolumeTemplates:
    - metadata:
        name: cti-collector-disk
      spec:
        # CRITICAL: Specify volumeMode: Block
        volumeMode: Block
        storage:
          accessModes:
            - ReadWriteOnce
          storageClassName: longhorn-kubevirt-block
          resources:
            requests:
              storage: 50Gi
        source:
          http:
            url: "https://cloud.debian.org/images/cloud/bookworm/latest/debian-12-generic-amd64.raw"
```

---

## 5. Comparative Performance Benchmarks

Running the identical `fio` benchmark profile on the RAW Block DataVolume produced dramatic performance gains:

| Metric | Filesystem (qcow2) | RAW Block DataVolume | Improvement |
| :--- | :--- | :--- | :--- |
| **Random 4K Read IOPS** | 3,450 IOPS | **14,800 IOPS** | **+328%** |
| **Random 4K Write IOPS** | 1,820 IOPS | **7,410 IOPS** | **+307%** |
| **Sequential Write Bandwidth** | 82 MB/s | **315 MB/s** | **+284%** |
| **Average Latency** | 17.5 ms | **4.3 ms** | **-75.4%** |
| **p99 Tail Latency** | 48.2 ms | **6.1 ms** | **-87.3%** |

### Key Takeaways
1. Always use `volumeMode: Block` for virtual machine root and data disks in KubeVirt.
2. Ingest raw disk images (`.raw` or `.img`) rather than `.qcow2` files when importing base OS cloud images.
3. Set `dataLocality: best-effort` in Longhorn to ensure that whenever possible, one storage replica resides on the same physical host executing the VM pod, minimizing intra-cluster network hops.
"""
    },

    "traefik-ingressroute-tls-port-80-drop-behavior": {
        "title": "Traefik v3 HTTP-to-HTTPS Redirection Pitfalls: Understanding Why IngressRoute Drops Port 80 Requests and How to Fix It",
        "excerpt": "Why defining an IngressRoute with TLS settings silently ignores HTTP port 80 traffic in Traefik v3, and the idiomatic way to configure global entryPoint HTTP-to-HTTPS redirects.",
        "markdown": """## 1. The Common Misconception

When publishing web applications on Kubernetes, developers naturally expect that entering `http://example.com` into a browser will automatically redirect to `https://example.com`. 

In Traefik v3, developers frequently create an `IngressRoute` manifest like this:

```yaml
apiVersion: traefik.io/v1alpha1
kind: IngressRoute
metadata:
  name: blog-emdash
  namespace: blog-stg
spec:
  entryPoints:
    - websecure
  routes:
    - match: Host(`blog-stg.lab.internal`)
      kind: Rule
      services:
        - name: blog-emdash
          port: 4321
  tls:
    secretName: lab-internal-wildcard-cert
```

Then, they test HTTP port 80 traffic:
```bash
curl -I http://blog-stg.lab.internal/
# Output:
# HTTP/1.1 404 Not Found (or connection refused)
```

The request fails with a **404 Not Found**! The user assumes their ingress is broken or their DNS is misconfigured.

---

## 2. Why Traefik IngressRoute Drops Port 80 Traffic

Traefik's routing model is built on strict separation of concerns:
- An **EntryPoint** is the physical network listener (`web` on port 80, `websecure` on port 443).
- A **Router** attaches to one or more specific EntryPoints.

In the manifest above, the `entryPoints` array contains only `websecure`. As a result:
1. Traefik registers the routing rule strictly on the HTTPS port 443 listener.
2. The HTTP port 80 listener (`web`) receives the incoming HTTP request.
3. Traefik checks all routers attached to the `web` entrypoint.
4. Because no router on `web` matches `Host(blog-stg.lab.internal)`, Traefik returns the default 404 handler or drops the connection.

---

## 3. The Anti-Pattern: Route-Level Redirect Middlewares

To "fix" this, developers often write duplicate IngressRoutes for every single service:
```yaml
# THE ANTI-PATTERN: DO NOT DO THIS FOR EVERY APPLICATION
apiVersion: traefik.io/v1alpha1
kind: IngressRoute
metadata:
  name: blog-emdash-http
spec:
  entryPoints: [web]
  routes:
    - match: Host(`blog-stg.lab.internal`)
      kind: Rule
      middlewares:
        - name: redirect-to-https
      services:
        - name: noop
```
Creating dozens of duplicate HTTP routers across every namespace is an operational nightmare that leads to configuration drift, clutter, and difficult debugging.

---

## 4. The Idiomatic Solution: Global EntryPoint Redirection

The proper, clean architecture is to configure **Global EntryPoint Redirection** at the gateway level. Instead of configuring redirection per-route, Traefik intercepts all traffic arriving on port 80 (`web`) and immediately redirects it to port 443 (`websecure`) before route evaluation occurs.

### Helm Configuration (`values.yaml`)
```yaml
ports:
  web:
    port: 8000
    exposedPort: 80
    redirectTo:
      port: websecure
      priority: 10
      permanent: true
  websecure:
    port: 8443
    exposedPort: 443
    tls:
      enabled: true
```

If configuring via command-line arguments:
```bash
--entrypoints.web.address=:80
--entrypoints.web.http.redirections.entrypoint.to=websecure
--entrypoints.web.http.redirections.entrypoint.scheme=https
--entrypoints.web.http.redirections.entrypoint.permanent=true
```

---

## 5. Handling the ACME HTTP-01 Challenge Exception

When using Let's Encrypt with HTTP-01 challenge verification, cert-manager or Traefik must receive validation tokens over plaintext HTTP port 80 (`/.well-known/acme-challenge/*`). 

If global entryPoint redirection is active, will it break ACME validation?
**No.** Traefik's internal router evaluates ACME HTTP-01 challenge paths with higher precedence than the redirection middleware, allowing ACME challenges to complete successfully while seamlessly redirecting all browser and API traffic to HTTPS.

---

## 6. Verification

```bash
# Test plaintext HTTP request
curl -vI http://blog-stg.lab.internal/
# Output:
# < HTTP/1.1 301 Moved Permanently
# < Location: https://blog-stg.lab.internal/

# Test curl following redirects
curl -ILs http://blog-stg.lab.internal/ | grep -E "HTTP/|location:"
# HTTP/1.1 301 Moved Permanently
# location: https://blog-stg.lab.internal/
# HTTP/2 200
```
Clean, unified, and zero boiler-plate manifests required per microservice.
"""
    }
}
