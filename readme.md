here’s a draft “working implementation” product spec for a dockerized, local-first demo stack that actually exercises the euridice jwg-api ig flows (inspect, find patient, patient summary via docs/resources, plus admin import/export). note: i’m basing this on the ci-build branch i could reliably open (branches/API-ig-draft) bc the /en/ url you pasted wouldn’t open via the web tool; if that branch diverges, treat this as ~95% right and adjust the config knobs.  ￼

⸻

0. product name

“euridice jwg-api sandbox” (working title, rename at will)

1. problem statement

you’ve got an ig that defines actors + transactions (t1 inspect, t2 find patient, doc + resource access patterns, optional oauth/iua, admin import/export), but rn it’s mostly “spec text + conformance artifacts.” you want a runnable demo that:
	•	is all local traffic first (single laptop, docker network)
	•	makes the transactions visibly real (requests, responses, logs, diagrams)
	•	stays simple as possible (no premature enterprise cosplay)
	•	still has an obvious path to “ok now put it behind real infra.”

the ig explicitly frames modular deployment (single fhir server vs a “virtual cloud” of service actors), so a docker-compose modular stack is aligned, not heresy.  ￼

2. goals (v0)
	1.	one-command bring-up: docker compose up yields a working sandbox.
	2.	demo the “happy path” flows:
	•	t1 inspect: GET <base>/metadata returns a capabilitystatement that advertises what you claim (doc vs resource access + priority areas).  ￼
	•	t2 find patient: GET/POST [base]/Patient?... works, including identifier search and supported-identifier hinting.  ￼
	•	eps patient summary (document path): consumer can query documentreferences and retrieve documents (mhd it i-67/66) with eps documentreference profile-ish examples seeded.  ￼
	•	eps patient summary (resource path): consumer can query resources (qedm/pcc-44 style “query existing data”) for the same patient.  ￼
	3.	admin flows:
	•	t4 import: minimal “required ui element” to upload example content into the provider.  ￼
	•	t5 export: minimal “required ui element” to export content (bulk export optional later).  ￼
	4.	optional auth mode: flip a flag and run with oauth2 (iua-ish), but keep “no auth” as default bc the ig allows it.  ￼
	5.	visualizer: show sequence + raw http + payloads per step (aka conformance theater, but useful).

3. non-goals (v0)
	•	full conformance to every option/priority area (lab, mpd, imaging, etc.)
	•	national infra / cross-border routing (only stubbed)
	•	deep consent/audit enforcement (log it, don’t boil the ocean)
	•	production hardening (this is a sandbox, not a device you ship into a hospital, lol)

⸻

4. primary personas
	•	spec author / editor (you): wants to validate the ig is implementable, catch ambiguity, and demo it to hl7 eu / stakeholders.
	•	implementer: wants a “copy this and run it” reference pattern.
	•	reviewer: wants to click through flows without reading 80 pages first.

the ig’s own “main use cases” call out admin, consumer, provider, patient, wellness app; we’ll implement admin + consumer + provider in v0, stub patient/wellness.  ￼

⸻

5. user stories + acceptance criteria

u1: inspect provider capabilities (t1)
	•	story: as a consumer app, i fetch provider metadata and learn what interfaces + priority areas exist.
	•	acceptance:
	•	GET /metadata returns 200 with a capabilitystatement
	•	response includes:
	•	fhir version r4 alignment (or clearly declares otherwise)
	•	declared “supports document access” + “supports resource access” (config-driven)
	•	declared supported priority areas (start with eps)
	•	visualizer shows request/response + timestamps.  ￼

u2: find patient (t2)
	•	story: as a consumer, i locate the patient i want before access.
	•	acceptance:
	•	GET /Patient?identifier=... returns bundle with matches
	•	provider publishes “supported identifier systems” in capabilitystatement (extension per ig guidance)
	•	both GET and POST search supported (POST can be “should” not “shall”, but do it anyway).  ￼

u3: patient summary via documents (mhd path)
	•	story: as a consumer, i find eps patient summary docs then retrieve them.
	•	acceptance:
	•	GET /DocumentReference?...patient=... returns eps-ish documentreferences
	•	retrieve a doc payload (binary or attachment) and render/download in the demo ui
	•	seeded sample: at least 1 eps patient summary per demo patient.  ￼

u4: patient summary via resources (qedm-ish path)
	•	story: as a consumer, i query discrete resources for the patient.
	•	acceptance:
	•	queries for at least: patient, encounter, condition, allergyintolerance, medication*, observation
	•	return bundles with realistic minimal examples (not 300kb nonsense)  ￼

u5: admin import (t4)
	•	story: as an admin, i upload eehrxf-formatted example content.
	•	acceptance:
	•	/admin/import web page exists
	•	upload a file (json bundle, or zip) and it lands in the fhir store
	•	import is limited to formats the provider claims support for (config gating).  ￼

u6: admin export (t5)
	•	story: as an admin, i export eehrxf data.
	•	acceptance:
	•	/admin/export lets me choose patient + “documents/resources/both”
	•	exports a zip with:
	•	fhir bundles (json) and/or ndjson (future)
	•	document payloads for doc-based exports
	•	optional later: $export bulk data path.  ￼

u7: optional oauth mode (iua-ish)
	•	story: as a consumer, i can run the same flows with oauth2 bearer tokens.
	•	acceptance:
	•	“auth: on” mode requires tokens for fhir endpoints
	•	capabilitystatement advertises auth endpoints/requirements (good enough for demo)
	•	keycloak issues tokens; reverse proxy enforces (or facade enforces)
	•	keep policy simple: role-based, not consent labyrinth.  ￼

⸻

6. architecture (local-first)

6.1 components (docker compose services)
	1.	reverse proxy (traefik or nginx)
	•	routes hostnames: fhir.local, demo.local, auth.local
	•	defaults: bind only to 127.0.0.1 (so “local traffic” is literal)
	2.	fhir server (hapi fhir jpa recommended for speed-to-demo)
	•	persistence: postgres
	•	stores: patients, resources, documentreference, binary
	3.	capability facade (thin service; fastapi or node)
	•	responsibility: serve a curated /metadata that matches ig semantics + your config, instead of whatever stock hapi emits
	•	optionally proxies other calls to hapi
	•	also hosts the admin ui for t4/t5
	4.	demo ui (static web app)
	•	“wizard” pages: inspect → find patient → list docs → retrieve doc → resource queries
	•	shows:
	•	mermaid sequence diagram for each flow
	•	raw http (headers, status)
	•	prettified json + diff vs expected profile snippets
	5.	auth server (optional): keycloak
	•	only enabled in “auth on” profile
	•	realm preloaded with demo clients + scopes
	6.	observability (optional-lite):
	•	simplest: structured logs + request correlation ids
	•	optional: otel collector + jaeger, but keep it off by default (bc it’s bloat rn)

this matches the ig’s point that “central services” can be single-server or modular cloud actors.  ￼

⸻

7. api surface (v0)

7.1 provider base urls
	•	https://fhir.local (reverse proxy → facade → hapi)
	•	https://auth.local (keycloak, optional)
	•	https://demo.local (demo ui)

7.2 implemented endpoints

t1 inspect
	•	GET /metadata → capabilitystatement (facade-generated)  ￼

t2 find patient
	•	GET /Patient?identifier=...
	•	POST /Patient/_search (optional but easy)  ￼

document path (eps patient summary)
	•	GET /DocumentReference?patient={id}&type={...}&status=current (minimal useful subset)
	•	GET /Binary/{id} (or direct attachment fetch)  ￼

resource path (qedm-ish)
	•	standard fhir searches, e.g.:
	•	GET /Condition?patient={id}
	•	GET /Observation?patient={id}&category=laboratory (later)
	•	etc.  ￼

admin ui (t4/t5)
	•	GET /admin/import + POST /admin/import
	•	GET /admin/export + POST /admin/export  ￼

⸻

8. data model + seed content

keep it aggressively tiny:
	•	2 demo patients:
	•	patient a: has 1 eps doc + a handful of resources
	•	patient b: same but different identifiers
	•	1 organization + 1 practitioner (optional)
	•	eps doc representation:
	•	DocumentReference conforming-ish to eps mhd documentreference profile
	•	Binary containing:
	•	either a fhir bundle “document” json
	•	or a pdf placeholder (if you want “real doc” vibes)

the seed should be deterministic and load on startup.

⸻

9. config (the “knobs”)

single config.yaml consumed by the facade:
	•	supported_priority_areas: [eps]  ￼
	•	interfaces: {document: true, resource: true}
	•	supported_identifier_systems:
	•	Patient: ["urn:oid:...","https://national.example/id"] (drives supported-identifier extension)  ￼
	•	auth: {enabled: false, issuer: ..., audience: ...}
	•	export: {mode: "ui" | "bulk"}  ￼

⸻

10. dockerization spec

10.1 repo layout
	•	/docker/compose.yml
	•	/services/facade (fastapi)
	•	/services/demo-ui (static)
	•	/services/seed (optional init container)
	•	/config/config.yaml
	•	/examples/ (fhir json)

10.2 compose profiles
	•	default (no auth):
	•	proxy, postgres, hapi, facade, demo-ui
	•	auth profile:
	•		•	keycloak
	•		•	proxy middleware to require bearer on /fhir/*

10.3 local-only networking
	•	publish ports only on localhost:
	•	127.0.0.1:8080 → proxy
	•	everything else internal on the docker network

⸻

11. security posture (v0)
	•	default: no auth (explicitly allowed by the ig; don’t pretend otherwise)  ￼
	•	auth mode:
	•	keycloak issues jwt
	•	facade validates jwt (or proxy does)
	•	scope names: keep aligned with your ig text (e.g. you’ve got a scope mention for t2: EHRsys-T2)  ￼
	•	no real consent rules in v0; just log “who asked for what” (bc audit is mentioned but not worth implementing deeply in a sandbox).  ￼

⸻

12. visualization requirements (this is the fun part)

demo ui shows, per flow:
	•	a mermaid sequence diagram with live populated urls/status codes
	•	a “curl equivalent” button
	•	request/response panes
	•	a conformance checklist panel that maps:
	•	“t1 uses GET /metadata”  ￼
	•	“t2 uses /Patient?<parameters>”  ￼
	•	“eps doc path uses iti-67/66”  ￼
	•	“t5 can be ui or bulk export”  ￼

minimum viable visualizer can be a single-page app with tabs; don’t overdesign it.

⸻

13. testing
	•	smoke tests (run in ci):
	•	bring up compose
	•	hit /metadata and assert fields exist
	•	create/find patient by identifier
	•	list documentreferences for patient
	•	retrieve binary
	•	export zip contains expected files
	•	contract-ish tests:
	•	jsonschema-ish checks for a couple key resources (documentreference, patient)

⸻

14. roadmap (how you “put it around other stuff” later)

v1 (still sane):
	•	add bulk data $export option for t5 (ndjson)  ￼
	•	add “cross-border api” stub endpoints (even if they 501) so diagrams show the boundary  ￼
	•	add a second “provider” instance to simulate federation (“virtual cloud”)  ￼

v2 (more real):
	•	plug in a real doc repository pattern (if you decide hapi-only is too fake)
	•	implement minimal audit event emission (even just audit logs as fhir audit events)
	•	start aligning capabilitystatement modularity (your own page notes the combinatorial explosion problem; use config-driven generation, not manual artifacts).  ￼

⸻

15. blunt critique (bc you asked)
	•	if you don’t build the capabilitystatement generator, your “inspect” transaction becomes decorative. stock servers rarely advertise the exact semantics you care about, and reviewers will dunk on it.
	•	don’t start by “full iua/smart” — you’ll drown in oauth minutiae and still not have a patient summary demo. ship the no-auth path first, then bolt on auth as a profile. the ig explicitly makes oauth conditional anyway.  ￼
	•	the admin t4/t5 being “ui elements” is a gift: it lets you implement import/export without bikeshedding bulk data on day 1.  ￼

⸻

if you want, next step i can turn this into a concrete “repo plan” with:
	•	docker-compose skeleton (services, networks, profiles)
	•	facade api contract (routes + data shapes)
	•	seed dataset outline (minimal jsons)
	•	demo ui page map + mermaid templates

(no waiting, no vibes, just files.)

⸻

16. ascii demo suite (implemented)

a claude-style terminal ui for running test cases with visual bounces and animations:
	•	location: /demo/ascii_demo.py
	•	features:
	•	claude-style formatted output (colors, boxes, code blocks)
	•	cute visual animations (bouncing dots, spinners, success bounces)
	•	full test suite covering t1-t5 transactions
	•	interactive or batch execution modes
	•	demo mode (shows ui without server connection)
	•	usage:
	•	python demo/ascii_demo.py --demo (preview ui)
	•	python demo/ascii_demo.py (run against server)
	•	python demo/ascii_demo.py --interactive (step through tests)
	•	integration: can be embedded in /services/demo-ui or run standalone