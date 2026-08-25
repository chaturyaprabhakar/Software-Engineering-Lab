# Domain & SSL Certificate Expiry Alert System

**Problem Statement #47** — Developer Tools & IT Operations

PES1UG24CS126 · SE Lab 1: Requirements Engineering & UML Use-Case Modelling

## 1. Problem Context

An IT operations utility that performs automated daily WHOIS registration and SSL/TLS handshake audits, alerting sysadmins through escalation ladders before domain or certificate expiration.

**Actors:** SysAdmin, Security Officer, Notification Gateway (external system)

## 2. Functional Requirements

| Req ID | Type | Description | Priority | Acceptance Criteria | Rationale |
|---|---|---|---|---|---|
| FR-001 | Functional | The system shall initiate TLS handshakes against monitored domains daily, extract certificate expiration dates, and trigger alerts at 30, 15, and 3 days before expiry. | High | Pass: Alert queued for a certificate expiring in 15 days. Fail: Expired certificate ignored without notification. | Certificate lapses cause outages and browser trust errors; a graduated warning ladder gives SysAdmins enough lead time to renew before impact. |
| FR-002 | Functional | The system shall perform daily WHOIS lookups on all monitored domains and trigger alerts at 30, 15, and 7 days before domain registration expiry. | High | Pass: WHOIS record showing 7 days to expiry produces a queued alert. Fail: A domain expiring within the window is skipped in the WHOIS scan. | Domain expiry is a distinct failure mode from certificate expiry (loss of the domain itself) and needs its own lead time, since registrar renewal can take longer than a cert renewal. |
| FR-003 | Functional | The system shall escalate an alert to the Security Officer if the SysAdmin has not acknowledged it within a configurable time window (default 24 hours). | High | Pass: An alert unacknowledged after 24 hours generates a second notification to the Security Officer. Fail: An unacknowledged alert stays only in the SysAdmin's queue indefinitely. | A single point of failure (one unresponsive SysAdmin) should not let a critical expiry go unhandled; escalation adds redundancy. |
| FR-004 | Functional | The system shall allow a SysAdmin to add, edit, remove, and bulk-import (CSV) domains and endpoints to the monitored list. | Medium | Pass: A CSV of 50 domains is imported and all 50 appear in the monitored list. Fail: Import silently drops malformed rows without reporting them. | Manual one-by-one entry doesn't scale for organizations managing many domains; bulk import is required for practical onboarding. |
| FR-005 | Functional | The system shall provide a dashboard showing the status (OK / Warning / Critical / Expired) of every monitored domain and certificate, filterable by status and owner. | Medium | Pass: Filtering by "Critical" shows only domains within 3 days of expiry. Fail: Dashboard shows stale data older than the last completed scan. | SysAdmins and Security Officers need a single point of visibility across the whole domain/certificate portfolio, not just individual alert emails. |

## 3. Non-Functional Requirements

| Req ID | Type | Description | Priority | Acceptance Criteria | Rationale |
|---|---|---|---|---|---|
| NFR-001 | Nonfunctional | The monitoring engine shall scan a list of 1,000 domains and SSL endpoints in under 3 minutes, using TLS 1.2+ for all outbound handshakes. | High | Pass: Benchmarking tests confirm target latency and security standards under simulated peak load. | Daily scans must complete well within a maintenance window; weak TLS versions during the scan itself would undermine the security purpose of the tool. |
| NFR-002 | Nonfunctional | The alerting pipeline shall achieve 99.5% successful delivery of due alerts per month, with failed deliveries automatically retried up to 3 times before being logged as a delivery failure. | High | Pass: Simulated notification-gateway outage results in automatic retry and an eventual delivery-failure log entry, not a silently dropped alert. | An alerting system that fails silently is worse than no alerting system — teams that trust it stop double-checking manually. |

## 4. UML Use-Case Diagram

![Use-case diagram](docs/use-case-diagram.png)

3 actors (SysAdmin, Security Officer, Notification Gateway), 5 primary use cases (UC-01–UC-05), with two «include» relationships (Perform Daily Scan → Check SSL & Domain Expiry; Send Alert → Authenticate Notification Channel) and one «extend» relationship (Escalate Alert extends Send Alert, when unacknowledged past 24h).

## 5. Use-Case Flow Specification

### Use Case: Perform Daily Scan

**Actors:** SysAdmin (configures schedule), System (executes scan)
**Includes:** Check SSL & Domain Expiry

**Preconditions**
- At least one domain/endpoint exists in the monitored list (see Configure Monitored Domains).
- The scanning engine has network connectivity to perform outbound WHOIS queries and TLS handshakes.
- The daily scan schedule is configured and active.

**Postconditions**
- Success: Every monitored domain and endpoint has an updated expiry record (domain registration date, certificate expiry date) and a status of OK, Warning, Critical, or Expired.
- Failure (partial): Domains/endpoints that could not be reached are flagged with a "scan failed" status and retained at their last known status rather than being silently dropped.

**Main Success Scenario**
1. The scheduler triggers "Perform Daily Scan" at the configured time.
2. The system retrieves the full list of monitored domains and endpoints.
3. For each entry, the system executes the included use case Check SSL & Domain Expiry: (a) performs a WHOIS lookup and extracts the domain registration expiry date; (b) initiates a TLS handshake and extracts the certificate expiry date.
4. The system computes days-remaining for both the domain and the certificate and classifies each as OK, Warning (≤30 days), Critical (≤3 days), or Expired.
5. The system persists the updated status for each entry and timestamps the scan.
6. The system passes any entry crossing an alert threshold (30/15/3 days for certificates, 30/15/7 days for domains) to the alerting pipeline (see Send Alert).
7. The system confirms scan completion and updates the dashboard's "last scanned" timestamp.

**Alternate Flow A1: Endpoint Unreachable During Scan**
Triggered at step 3 if a TLS handshake or WHOIS lookup times out or fails.
- A1.1 — The system logs the failure reason (timeout, connection refused, DNS resolution failure, etc.) against that entry.
- A1.2 — The system retains the entry's last known status rather than overwriting it with an error state.
- A1.3 — The system flags the entry as "scan failed" on the dashboard for SysAdmin visibility.
- A1.4 — The system continues scanning the remaining entries in the list (a single failure does not halt the batch).
- A1.5 — Resume at step 4 of the main flow for all other entries.

*Performance note: Per NFR-001, the full batch (up to 1,000 domains/endpoints) must complete within 3 minutes; scans are parallelized across entries to meet this bound.*
