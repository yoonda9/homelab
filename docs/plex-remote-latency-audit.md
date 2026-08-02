# Audit: where remote Plex latency actually comes from

Deliverable for Steps 2 and 3 of the Plex optimization plan
(`.agents/planning/2026-07-27-plex-optimization/implementation/plan.md`). Both steps proposed
changes to Traefik. This audit measured the path first, and the measurement says **no change to
Traefik is warranted** — the reverse proxy is not where the time goes, and it is already
configured optimally on every dimension the plan named.

"No change warranted, here is the evidence" is the honest outcome of an audit. It is recorded
here rather than acted on, because acting on Step 2 as written would mean deleting the only
hardening middleware on this repo's only WAN-exposed router.

Evidence: the external capture of 2026-07-28T02:43:04Z (`logs/plex-latency.jsonl`, label
`baseline`, vantage `external`), the LAN control in the same file (label `baseline-smoke`), and
the connection-phase decomposition in §3.

---

## 1. Step 2 — the middleware chain, audited

Every middleware reachable from the two Plex routers in
`ansible/roles/docker_host/templates/dynamic.yml.j2`:

| router | entrypoint | middlewares | keep/drop | why |
|---|---|---|---|---|
| `plex` | `websecure` | `security-headers@file` | **KEEP** | Response-header setter only: HSTS, `contentTypeNosniff`, `browserXssFilter`, `frameDeny`, `referrerPolicy`. It writes six headers onto the response. It does not buffer, inspect a body, authenticate, or rate-limit. Its cost is not measurable against a 157 ms floor, and it is the only hardening on this repo's only WAN-public router. |
| `plex-web` | `web` | `redirect-to-https@file` | **KEEP** | Issues a 301 to HTTPS. Only plaintext `:80` requests traverse it; a client already on `https://` never touches it. Removing it would downgrade, not accelerate. |

Two further facts the audit establishes by absence:

- **`internal-allowlist@file` is deliberately NOT on either Plex router.** That is by design — Plex
  is the only router reachable from the WAN. There is no allowlist evaluation in the Plex path to
  remove.
- **No `buffering` middleware is defined anywhere in `dynamic.yml.j2`.** Step 3's requirement to
  "confirm no buffering middleware is in the path" is satisfied by absence, not by a change.

The chain is two middlewares, one per entrypoint, each doing the minimum. There is nothing to
simplify. `test_traefik_config_shape.py::test_plex_router_is_public_not_allowlisted` already pins
this shape; it should stay as-is.

## 2. Step 3 — TLS and HTTP versions, verified live

No `tlsOptions` block exists in `traefik.yml.j2` or `dynamic.yml.j2`, so Traefik runs its
defaults. Verified from the external vantage against the live endpoint:

```
$ curl -o /dev/null -s -w 'http=%{http_version}\n' https://plex.yoonnation.com/identity
http=2
$ curl -o /dev/null -sv https://plex.yoonnation.com/identity 2>&1 | grep -i "SSL connection\|ALPN"
* ALPN: server accepted h2
* SSL connection using TLSv1.3 / TLS_AES_128_GCM_SHA256 / X25519 / RSASSA-PSS
```

TLS 1.3 (1-RTT handshake, not 1.2's 2-RTT), HTTP/2 negotiated via ALPN, X25519 key agreement,
AES-128-GCM. This is the configuration a `tlsOptions` block would have been written to produce.
**Pinning it explicitly would change nothing and would freeze a default that should track
Traefik's upstream.** No change made.

## 3. Where the time actually goes

`curl` connection-phase decomposition, same external vantage, five consecutive samples of
`/identity` (ms, derived by subtracting the cumulative timings):

| sample | DNS | TCP (1 RTT) | TLS | server wait | TTFB | setup share |
|---|---|---|---|---|---|---|
| 1 | 63.9 | 457.2 | 311.3 | 201.7 | 1034.1 | 80% |
| 2 | 29.1 | 116.2 | 109.0 | 75.3 | 329.6 | 77% |
| 3 | 22.1 | 46.6 | 425.2 | 110.0 | 603.9 | 82% |
| 4 | 80.1 | 275.2 | 203.4 | 98.2 | 656.9 | 85% |
| 5 | 53.1 | 155.5 | 291.9 | 94.6 | 595.1 | 84% |

**Connection setup — DNS + TCP + TLS — is 77–85% of every sample.** None of it is reachable from
this repo: DNS resolution happens at the client's resolver, and the TCP and TLS handshakes are
round trips whose duration is the mobile link.

The remaining "server wait" column is itself mostly a round trip — it spans from TLS completion
to the first response byte, so it contains one RTT plus Plex's thinking time. The cleanest bound
available: sample 3 pairs a **46.6 ms** TCP RTT with a **110.0 ms** server wait, and sample 2 a
116.2 ms RTT with a 75.3 ms wait. Plex's own work is on the order of **tens of milliseconds**,
consistent with the LAN A/B, where the entire Traefik hop measured **+9.4 ms** median TTFB
(9.728 ms via Traefik vs 0.327 ms direct to `192.168.1.110:32400`).

So the budget for a cold remote request is roughly: ~500 ms of network handshakes, ~10 ms of
Traefik, ~20–30 ms of Plex.

## 4. The finding that also invalidates Step 4

TCP connect is a single round trip and therefore the cleanest RTT measurement in the set. Across
five consecutive samples it ranged **46.6 ms to 457.2 ms — a 10x spread, seconds apart.**

Sample 4 pairs a 275.2 ms RTT with a 98.2 ms server wait, which is impossible for a stable link:
the round trip is moving underneath the measurement faster than the measurement completes.

This is a property of the transport, not of the harness. Its consequence is structural:

> Step 4 proposes to detect the improvement from Steps 2–3 by diffing this baseline against a
> post-change re-measurement. The largest effect those steps could produce is bounded by
> Traefik's total contribution, **~10 ms**. The instrument's sample-to-sample variance on this
> link is **several hundred milliseconds**. Ten samples cannot resolve a 10 ms effect against
> that noise floor.

No amount of additional rigor on `measure_plex_latency.py` changes this — the variance is in the
link, not the code. A comparison run anyway would produce a number, and that number would be
noise with a sign.

## 5. Conclusions

1. **Step 2: no removal warranted.** The chain is `security-headers` on `plex` and
   `redirect-to-https` on `plex-web`. Both are minimal and both are justified. The plan's premise
   — that heavy middlewares are slowing remote Plex — is false for this repo.
2. **Step 3: no change warranted.** TLS 1.3 and HTTP/2 are already negotiated; no buffering
   middleware exists in the path. Verified live rather than assumed.
3. **Step 4 cannot be run as specified.** Its effect size is ~50x below its instrument's noise
   floor. It should not be executed as a pass/fail on the Traefik changes, because it would
   manufacture a verdict rather than measure one.
4. **The reverse-proxy track is closed by measurement.** Traefik accounts for under 2% of a cold
   remote request.

## 6. Where the real lever is

The complaint being optimized is remote Plex feeling slow, and what a household actually
perceives is **video**, which does not traverse the path measured above the same way. The
decisive question is whether remote streams are served **Direct** or via **Plex Relay** — Relay
proxies through plex.tv's servers and caps around 2 Mbps, which would make streaming feel bad
regardless of anything in this repo.

That is a reachability question about port `32400` and Plex's own Remote Access settings, not a
Traefik question. It is operator-side and unmeasured as of this audit.

**Recommended next step, replacing Steps 2–4:** start a remote stream and read Direct vs Indirect
off the Plex dashboard. If it says Indirect, that single finding is worth more than the entire
reverse-proxy track this audit just closed.
