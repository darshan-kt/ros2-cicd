# CD Pipeline Tools

What each tool in the deployment path actually does, why it's the one used
here, the commands you'll actually reach for, and how it connects to the
others. Companion to [`CD-pipeline-strategy.md`](CD-pipeline-strategy.md),
which covers the order things were built in — this one is the reference
for each individual piece.

---

# How they connect

```text
DockerHub  <───────────────┐
   ▲                       │ pulls images
   │ pushes images         │
   │                       │
GitHub Actions          Kubernetes (minikube)
(CI + CD jobs)              ▲  ▲  ▲
   │                        │  │  │
   │ pushes commits         │  │  └── kubectl: talks to the API server directly
   ▼                        │  │
GitHub repo                 │  └───── Helm: renders + (optionally) applies charts
(source of truth)           │
   │                        └──────── ArgoCD: pulls from git, applies via
   │ polled by ArgoCD                 the same API server, from inside the cluster
   └────────────────────────┘

Ingress (nginx), inside Kubernetes, is what a browser actually talks to —
it routes ros2.local / api.ros2.local to the frontend/backend Services.
```

The one-line version: **DockerHub moves images, git moves desired state,
ArgoCD moves desired state into the cluster.** Nothing but ArgoCD ever
needs credentials for the cluster itself.

---

# Kubernetes

**What it is:** a container orchestrator — given a declarative spec
("2 replicas of this image, on this port"), it keeps that many healthy
containers running, restarts ones that crash, and load-balances traffic
across them via Services.

**Why it's here:** Docker Compose (also in this repo) runs one instance of
each service on one host. Kubernetes is what makes "2 backend replicas,
automatically replaced if one dies, only receiving traffic once its
readiness probe passes" possible at all.

**Key objects used in this project:**

| Object | Used for |
| --- | --- |
| `Deployment` | keeps N Pods of an image running (`backend`, `frontend`, `ros2`) |
| `Service` | stable internal address for a Deployment's Pods (`backend-service`) |
| `Ingress` | routes external hostnames to Services (`ros2.local` → `frontend-service`) |
| `ConfigMap` / `Secret` | environment variables injected via `envFrom` |
| `Namespace` | isolates this app's resources (`cicd-demo`) |

**Basic commands:**

```bash
kubectl get pods -n cicd-demo                  # what's running
kubectl logs -n cicd-demo deploy/backend        # why isn't it working
kubectl describe pod <name> -n cicd-demo        # events, probe failures
kubectl exec -n cicd-demo deploy/backend -- env # what env actually landed
kubectl rollout status deployment/backend -n cicd-demo
kubectl rollout undo deployment/backend -n cicd-demo   # emergency rollback
```

**minikube** is the specific Kubernetes distribution used here — a single
node running locally in a Docker container, chosen because it needs no
cloud account and its bundled pod networking happens to pass DDS multicast
(see the strategy doc's Phase 4). `minikube ip`, `minikube addons enable
ingress`, and `minikube image load <tag>` (load a locally built image
without pushing to a registry) are the commands specific to it, as
opposed to any other Kubernetes cluster.

---

# Helm

**What it is:** a templating engine and package manager for Kubernetes
manifests. A "chart" is a directory of YAML templates plus a
`values.yaml` of parameters; `helm template` (or an install/upgrade)
renders the templates with those values substituted in.

**Why it's here:** writing `kubectl apply -f` against seven hand-edited
YAML files (one per resource) doesn't scale and has no concept of "this is
one versioned release." Helm turns that into one chart, one values file,
one command. In this project specifically, it's also what makes the image
tag bump in the CD pipeline a one-line edit (`values.yaml`) instead of
editing several Deployment manifests.

**Basic commands:**

```bash
helm lint helm/ros2-cicd                        # catches template mistakes
helm template ros2-cicd helm/ros2-cicd           # render to plain YAML, don't apply
helm template ros2-cicd helm/ros2-cicd | kubectl diff -f -   # render + diff against live cluster, no changes made
helm install ros2-cicd helm/ros2-cicd -n cicd-demo
helm upgrade --install ros2-cicd helm/ros2-cicd -n cicd-demo
helm list -n cicd-demo                           # installed releases
helm rollback ros2-cicd <revision> -n cicd-demo
```

**How it connects:** ArgoCD doesn't shell out to the `helm` binary — it
has its own built-in Helm template renderer, pointed at
`helm/ros2-cicd` via `argocd/application.yaml`'s `source.path`. The `helm`
CLI itself is a local development tool here (linting, diffing, one-off
manual installs); the cluster's actual desired state is applied by ArgoCD.

---

# ArgoCD

**What it is:** a GitOps continuous-delivery controller. It runs *inside*
the cluster, watches one or more git repos, and continuously reconciles
the cluster to match what's declared there — including reverting manual
`kubectl edit` changes that drift from git, if `selfHeal` is on.

**Why it's here:** it's the piece that makes "GitHub Actions can't reach a
local minikube cluster" a non-problem. Instead of CI pushing changes in,
ArgoCD pulls them, from inside the network the cluster already trusts. It
also turns every deploy into an auditable git commit instead of an
ephemeral `kubectl apply` no one can replay.

**Core object:** `Application` (`argocd/application.yaml`) — declares
which repo/path to watch (`helm/ros2-cicd` on `master`), which
namespace to deploy into (`cicd-demo`), and the sync policy:

```yaml
syncPolicy:
  automated:
    prune: true      # remove resources deleted from git
    selfHeal: true    # revert manual cluster drift back to match git
```

**Basic commands:**

```bash
argocd login localhost:8081 --username admin        # after port-forwarding argocd-server
argocd app get ros2-cicd                             # sync/health status, resource tree
argocd app sync ros2-cicd                             # force a sync now, don't wait for the poll interval
argocd app history ros2-cicd                           # past syncs, for rollback

# equivalent read-only checks via plain kubectl, no argocd CLI needed:
kubectl get application ros2-cicd -n argocd
kubectl get application ros2-cicd -n argocd -o jsonpath='{.status.sync.status} {.status.health.status}'
```

**How it connects:** ArgoCD polls the GitHub repo the CD job pushes to; it
renders `helm/ros2-cicd` itself (no separate `helm` install needed inside
the cluster); it applies the rendered manifests via the same Kubernetes
API server `kubectl` talks to — ArgoCD has no special access path, it's
just another authenticated client of the API server, running in-cluster
with a ServiceAccount instead of a laptop's kubeconfig.

---

# NGINX Ingress Controller

**What it is:** a reverse proxy running as a Pod inside the cluster,
watching `Ingress` resources and configuring itself (an actual nginx
config, reloaded live) to match them.

**Why it's here:** without it, every Service needs its own `NodePort` —
a different port number per app, awkward to remember and to share.
Ingress collapses that to one entry point on port 80, routed by hostname:
`ros2.local` → frontend, `api.ros2.local` → backend.

**Basic commands:**

```bash
minikube addons enable ingress          # installs the controller (minikube-specific)
kubectl get pods -n ingress-nginx        # confirm it's Running
kubectl get ingress -n cicd-demo         # what hosts/paths are configured
```

**How it connects:** it's the actual thing a browser talks to. It's
*inside* Kubernetes like everything else here, deployed and watched the
same way — the `Ingress` resource that configures it (`k8s/ingress.yaml`
→ `helm/ros2-cicd/templates/ingress.yaml`) is itself managed by ArgoCD,
same as the Deployments and Services.

---

# yq

**What it is:** a command-line YAML processor — think `jq`, but for YAML
instead of JSON.

**Why it's here:** the CD job needs to edit exactly one field
(`backend.image.tag`) in `values.yaml` without disturbing anything else
around it (comments, formatting, unrelated keys). `sed` can do this but is
fragile against YAML's structure; `yq` understands the document as YAML.

**The one command that matters here:**

```bash
yq -i '.backend.image.tag = "abc123"' helm/ros2-cicd/values.yaml
```

`-i` edits in place — this is the exact line the `cd` job in
`.github/workflows/ci.yml` runs, once per image (backend, frontend).

---

# GitHub Actions (the `cd` job specifically)

The `ci` job (lint, test, build, push images) is standard CI and not
unique to this doc. The `cd` job is the piece that's specifically about
deployment:

```yaml
cd:
  needs: ci
  if: github.event_name == 'push'
  permissions:
    contents: write
  steps:
    - checkout
    - install yq
    - bump image tags in helm/ros2-cicd/values.yaml
    - git commit -m "... [skip ci]" && git push
```

**Why it only writes to git, never to the cluster:** giving a cloud CI
runner direct `kubectl` access to the cluster would mean either exposing
a local minikube to the internet, or storing a cluster credential in
GitHub secrets that every workflow run (and anyone with repo write access)
could reach. Writing to git and letting ArgoCD pull avoids both.

**Why `[skip ci]` matters:** the `cd` job's own push would otherwise
retrigger the whole workflow — including another `cd` job — indefinitely.
GitHub Actions natively skips triggering a workflow for any push whose
head commit message contains `[skip ci]`.

---

# DockerHub

**What it is:** the container registry both `docker build` output and
Kubernetes' image pulls go through.

**Why it's here:** Kubernetes doesn't build images, it only pulls them
from somewhere. CI builds locally on the runner and needs somewhere to
publish for the cluster to later pull from — DockerHub is that shared
handoff point, decoupling "when an image is built" from "when it's
deployed" (which, in this pipeline, can be minutes or days apart, whenever
ArgoCD's poll picks up the tag bump or a `sync` is forced).

**Images in this project:** `ros2-monitoring`, `ros2-backend`,
`ros2-frontend`, each tagged with the git commit SHA of the build — never
`:latest`, so `values.yaml` pinning a specific tag is always reproducible
and traceable back to an exact commit.
