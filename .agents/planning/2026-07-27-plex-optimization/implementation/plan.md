# Implementation Plan: Plex Remote Optimization

## Checklist
- [ ] Step 1: Baseline Performance Measurement
- [ ] Step 2: Audit and Simplify Traefik Middlewares for Plex
- [ ] Step 3: Optimize Traefik Buffering and Header Settings
- [ ] Step 4: End-to-End Validation and Final Performance Measurement

## Implementation Steps

### Step 1: Baseline Performance Measurement
**Objective:** Establish a clear performance baseline to measure the impact of subsequent optimizations.
**General Implementation Guidance:** Before making any infrastructure changes, use a browser network inspector or `curl` to capture the Time to First Byte (TTFB) and total load time for initial Plex API requests via `plex.yoonnation.com`. Record these metrics.
**Test Requirements:** Ensure that metrics are gathered from an external network (e.g., via a mobile hotspot) to accurately simulate remote connection behavior.
**Integration:** This forms the foundation against which all future steps will be compared.
**Demo:** A documented set of baseline metrics showing current UI/library load times and API latency.

### Step 2: Audit and Simplify Traefik Middlewares for Plex
**Objective:** Remove or bypass any heavy Traefik middlewares (such as complex authentication, unnecessary header modifications, or rate limiting) that apply to the Plex router.
**General Implementation Guidance:** Locate the Traefik dynamic configuration or Ansible role responsible for `plex.yoonnation.com`. Comment out or remove any middlewares that are not strictly necessary for basic SSL termination.
**Test Requirements:** After deploying the configuration change, verify that `https://plex.yoonnation.com` still loads correctly and that no essential security (like SSL) is broken.
**Integration:** Builds on the baseline by taking the first concrete step to reduce proxy overhead.
**Demo:** The Plex web interface is successfully accessed remotely with a simplified middleware chain, and no 404/500 errors are observed in the Traefik logs.

### Step 3: Optimize Traefik Buffering and Header Settings
**Objective:** Configure Traefik specifically for high-throughput, long-lived connections required by Plex.
**General Implementation Guidance:** Add or adjust Traefik configurations to pass through standard proxy headers (e.g., `X-Forwarded-For`, `X-Forwarded-Proto`). Ensure WebSockets (used by Plex) are properly supported by the router, and disable any buffering middleware that might choke large API/metadata loads.
**Test Requirements:** Restart Traefik and load the Plex library. Verify that WebSocket connections establish successfully without dropping.
**Integration:** Refines the simplified route created in Step 2 by adding Plex-specific optimizations.
**Demo:** A remote user can load the Plex app and establish stable WebSocket connections (visible in network inspector), with Traefik correctly passing client IP addresses to the Plex dashboard.

### Step 4: End-to-End Validation and Final Performance Measurement
**Objective:** Verify that the optimizations have successfully reduced initial library load times without breaking direct playback.
**General Implementation Guidance:** Repeat the latency measurements taken in Step 1. Compare the new TTFB and total load times against the baseline. Also, initiate a media stream and verify via the Plex Dashboard that the connection is listed as "Direct" on port 32400.
**Test Requirements:** The final API load times should be demonstrably lower than the baseline. The media stream must not fall back to "Relay".
**Integration:** Wires together the optimizations from Steps 2 and 3 and compares them against the Step 1 baseline.
**Demo:** A final demonstration showing a faster, snappier initial library load from a remote client, alongside a log of the Plex Dashboard showing a healthy "Direct" streaming connection.
