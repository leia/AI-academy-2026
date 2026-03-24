# Clarified Examples

<!--
source: curated
type: example
tags: clarified, reference
version: 2026-03-24
-->

## Example 1
- **Original:** Improve dashboard UX and fix login issue before release.
- **Clarified:** Address top 3 usability complaints on the dashboard (navigation, filter reset, tooltip clarity) and resolve the intermittent SSO login failure for Okta users. Target completion before the April 15 release; success measured by <2% login error rate and user test SUS >75.

## Example 2
- **Original:** Build mobile push notifications for critical alerts with a 5-minute delivery SLA.
- **Clarified:** Send push notifications to on-call engineers for P1 incidents within 5 minutes 95% of the time, using Firebase for Android and APNs for iOS. Include deep links to incident runbooks; add opt-in controls and quiet hours. Track delivery latency and open rates in Grafana.

## Example 3
- **Original:** Migrate reporting service to the new data warehouse without downtime.
- **Clarified:** Dual-write to Snowflake and legacy warehouse for two weeks; cut over via feature flag after parity validation on top 20 reports. Define rollback path within 30 minutes; no visible downtime allowed during EU business hours (08:00–18:00 CET).
