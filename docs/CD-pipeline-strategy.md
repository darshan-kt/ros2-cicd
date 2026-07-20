# CD Pipeline Strategy

How this project went from "CI builds images" to "push to master and the
cluster updates itself" — in the order it actually happened, including the
dead ends and the bugs found along the way.

---

# Starting Point

Before any of this, the pipeline stopped at CI:

```text
git push
    │
    ▼
GitHub Actions
  lint / test / coverage / security scan
  build ros2 / backend / frontend images
  push to DockerHub
```

Getting a new image actually running meant SSH-ing into wherever the
cluster lived and running `kubectl apply` or `helm upgrade` by hand. That's
the gap this strategy closes.

---

# Phase 1 — Helm: package what already exists

**Goal:** convert the plain manifests in `k8s/` into a Helm chart, with
zero behavior change, before adding anything new on top.

Steps:

1. Write `helm/ros2-cicd/` with the same resource *names* as the existing
   manifests (`backend`, `frontend-service`, `ros2-ingress`, ...). Same
   names matters — it's what let this become an adoption instead of a
   parallel deployment.
2. Validate before touching the cluster:
   ```bash
   helm lint helm/ros2-cicd
   helm template ros2-cicd helm/ros2-cicd | kubectl diff -f -
   ```
   `kubectl diff` against the live cluster is the important one — it
   proves the chart renders to *exactly* what's already running, field for
   field, before it ever gets applied.
3. Adopt the existing resources into Helm's ownership instead of deleting
   and recreating them:
   ```bash
   kubectl annotate <kind> <name> -n cicd-demo \
     meta.helm.sh/release-name=ros2-cicd \
     meta.helm.sh/release-namespace=cicd-demo --overwrite
   kubectl label <kind> <name> -n cicd-demo \
     app.kubernetes.io/managed-by=Helm --overwrite
   ```
4. `helm install ros2-cicd helm/ros2-cicd -n cicd-demo` — because the diff
   was already zero and the resources were pre-adopted, this caused **zero
   pod restarts**. Confirmed by checking pod `AGE` didn't reset.

**Bug found while doing this:** `k8s/backend/deployment.yaml`'s `envFrom`
had `secretRef.name` indented as a *sibling* of `secretRef` instead of
nested under it — valid YAML, wrong structure. `secretRef` silently
evaluated to empty, and `API_KEY`/`JWT_SECRET` were never actually
injected into the pod. `kubectl exec ... env` confirmed the variables were
missing. Fixed as part of the chart conversion.

---

# Phase 2 + 3 — CD, merged with GitOps from the start

The original plan (mirroring a common tutorial progression) was:

* Phase 2: GitHub Actions runs `helm upgrade` directly against the cluster
* Phase 3: switch that to GitOps with ArgoCD later

That plan doesn't survive contact with this project's actual constraint:
**the cluster is a local minikube instance.** GitHub's cloud-hosted runners
have no network path to it. Phase 2 as originally scoped is not just
harder here, it's impossible without a self-hosted runner or exposing a
local machine to the internet.

So Phases 2 and 3 were combined into one pull-based design from the start:

```text
GitHub Actions (CI)
  build + push images, tagged with the commit SHA
       │
       ▼
GitHub Actions (CD)
  yq: bump helm/ros2-cicd/values.yaml image tags to the new SHA
  git commit -m "... [skip ci]"
  git push
       │
       ▼
GitHub repo                 <- desired state lives here, not in the cluster
       │
       │  ArgoCD polls this repo FROM INSIDE the cluster
       ▼
ArgoCD renders the chart, applies it, self-heals drift
```

The CD job never receives cluster credentials. It only needs push access
to the same repo the workflow already checked out. ArgoCD is the only
thing that ever talks to the Kubernetes API for deployment purposes, and
it does so from inside the cluster, pulling — nothing reaches in from
outside.

**The loop-prevention detail:** the CD job's own commit re-triggers `push`,
which would re-trigger CI, which would re-trigger CD, forever. Fixed with
`[skip ci]` in the bump commit's message — GitHub Actions natively skips
workflow runs for commits containing that marker.

**Adoption gap this revealed:** ArgoCD doesn't automatically manage
resources someone else's tooling already owns. `helm install` from a
laptop and `helm install` from ArgoCD's internal Application controller
are two different "owners" as far as Helm's release tracking is concerned.
In this project that wasn't a real conflict (ArgoCD applies resources
directly rather than fighting Helm CLI's release Secret), but it's the
reason the very first `helm install` in Phase 1 was done manually before
`argocd/application.yaml` ever existed — establishing the known-good state
first, then pointing GitOps at it, rather than the other way around.

---

# Phase 4 — Deploy ROS2 into the cluster

Deliberately last. Everything above (Helm, the CD job, ArgoCD) had to be
proven working on two components (frontend, backend) before adding the one
with the least predictable networking behavior.

**The actual risk:** ROS2's default DDS discovery (SIMPLE discovery
protocol) uses UDP multicast. Kubernetes overlay networks (Calico, Cilium,
etc.) commonly block multicast by default. If discovery didn't work, the
backend's `/ready` endpoint — which checks real ROS2 connectivity, not
just process liveness — would 503 forever, and a readiness probe wired to
it would take down the Service's endpoints.

**How it was actually validated**, in order:

1. Paused ArgoCD's automated sync (`syncPolicy` removed from the
   Application) so manual iteration wouldn't get reverted mid-test:
   ```bash
   kubectl patch application ros2-cicd -n argocd --type=json \
     -p='[{"op":"remove","path":"/spec/syncPolicy"}]'
   ```
2. Added the `ros2` Deployment to the chart with `backend.probes.enabled`
   still `false` — so if discovery failed, the backend wouldn't get killed
   by a failing liveness probe while being debugged.
3. Built and loaded the image directly into minikube for a fast local
   iteration loop, bypassing DockerHub and git entirely for this step:
   ```bash
   docker build -f docker/ros2.Dockerfile -t ros2-monitoring:local .
   minikube image load ros2-monitoring:local
   helm upgrade --install ros2-cicd helm/ros2-cicd -n cicd-demo
   ```
4. Checked `/health` from outside the cluster. It came back
   `{"publisher":true,"subscriber":true,"system":true}` on the first try —
   minikube's single-node setup uses a plain Linux bridge for its pod
   network, not an overlay/VXLAN CNI, and plain bridges pass multicast
   fine. No `ROS_STATIC_PEERS` workaround or rosbridge fallback needed.
5. Only *then* flipped `backend.probes.enabled: true` and confirmed a
   rolling update completed cleanly with the readiness probe actually
   gating traffic.
6. Committed the validated chart + values, pushed, let the real CD/GitOps
   loop take over, then re-enabled ArgoCD's automated sync and confirmed
   it swapped the local test images for the official CI-built ones with
   zero downtime.

**Two more bugs found during end-to-end validation** (neither one visible
under Docker Compose, both only visible once traffic went through the
Kubernetes ingress):

* `frontend/app.js` assumed the backend is always reachable at
  `${hostname}:8000` — true for Docker Compose (same host, different
  port), false for the ingress (`api.ros2.local` vs `ros2.local`,
  different **hostname**, same port). Fixed by branching on whether the
  page's own hostname ends in `.local`.
* The backend's CORS `allow_origins` list didn't include
  `http://ros2.local`, so the dashboard's `/health` `fetch()` was silently
  blocked by the browser. The WebSocket connection worked anyway (it isn't
  CORS-gated), which is exactly why this one was easy to miss — the
  counters were live-updating while the health pill said "Unreachable."

---

# What "ship a change" looks like now

```text
edit code
    │
    ▼
git push
    │
    ▼
CI: lint, test, coverage, security scan, build, push images
    │
    ▼
CD: bump image tags in helm/ros2-cicd/values.yaml, commit, push
    │
    ▼
ArgoCD notices the commit, renders the chart, applies it
    │
    ▼
new Pods roll out once they pass their readiness probe,
old Pods terminate
```

No step in that chain is a person running `kubectl` or `helm` by hand.
That's the strategy: push deploy-time decisions (what image, what config)
into git, and let a controller *inside* the cluster be the only thing with
apply access, rather than granting that access to CI.

---

# Rollback

Because desired state is a git commit, rollback is a git operation:

```bash
git revert <bad-commit>
git push
```

ArgoCD picks up the revert the same way it picks up any other commit.
Whatever `values.yaml` said before the bad change is what gets
re-deployed — no manual image-tag archaeology needed.

---

# What's deliberately not done yet

* **Blue-green / canary rollouts** — right now a "bad" deploy still
  briefly serves from new Pods before the readiness probe would catch a
  real failure. Progressive delivery (Argo Rollouts, or a service mesh)
  is the next step for that.
* **Observability** — Prometheus/Grafana aren't wired in. Right now
  "healthy" means the probes pass; there's no dashboard for latency,
  error rate, or DDS discovery flakiness over time.
* **Self-hosted runner** — the pull-based GitOps design sidesteps needing
  one, but it also means CI genuinely cannot deploy on its own in an
  emergency; ArgoCD (and the cluster being reachable) is a hard
  dependency for anything to roll out.
