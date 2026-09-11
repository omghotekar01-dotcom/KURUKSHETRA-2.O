# EVENT AND CONSTRAINTS — KURUKSHETRA 2.0 HACKFEST 2026

Last updated: 2026-09-11

This file contains only event facts already supplied/verified for this project. If an organizer later changes anything, update this file and record the change in `DECISION_LOG.md` / `docs/PROJECT_STATUS.md` when it affects execution.

## Event

- Name: **Kurukshetra 2.0 Hackfest 2026**
- Organizer: **MIT Arts, Commerce & Science College, Alandi, Pune, Maharashtra**
- Mode: **Offline**
- Venue: MAEER'S MIT Arts, Commerce and Science College, Alandi–Moshi Road, opposite Gajanan Maharaj Sansthan, Alandi, Pune, Maharashtra 412105
- Dates: **11–12 September 2026**
- Duration: **24 hours**
- Team size allowed: **1–4 members**
- Our team size: **4 members**
- Prize pool listed: **₹1,00,000+**
- Total winners listed: **9**, described as 3 winners from each domain
- Event themes described publicly include AI/ML, Web3, cloud computing and automation; the exact released problem statement remains the controlling requirement.

## Check-in / event schedule supplied by organizers

- Registration/check-in starts: **8:00 AM sharp, 11 September**
- Inauguration: **10:00 AM sharp**
- Inauguration attendance: compulsory for all teams
- Problem statements release: **11:00 AM sharp**, after inauguration

## Physical requirements supplied by organizers

Each participant/team should be prepared with:

- filled and signed hard copy of undertaking/consent form for every team member;
- team QR code for scan/confirmation;
- valid government ID;
- college ID recommended.

## Engineering constraint implied by the event

The practical product-development window is approximately 24 hours. Therefore every architecture decision must be judged against:

1. time to first working end-to-end flow;
2. integration risk across four developers;
3. dependency on fragile external APIs/services;
4. ability to demo deterministically;
5. ability to explain the value within a short judging interaction;
6. ability to produce credible metrics/evidence within the event;
7. reproducibility from a fresh clone.

## Team process constraint

The project is built collaboratively through GitHub.

Canonical branch policy:

- `main` = stable/demo/submission only;
- `develop` = shared integration;
- dedicated/personal branches currently include `OM-G`, `OM-PATIL`, `NIKHIL`, `YASH`;
- scoped feature/fix/docs/test branches may be used where cleaner;
- normal path is personal/feature branch -> PR -> `develop` -> tested release -> `main`.

See `docs/TEAM_README.md` for commands and safety rules.

## Non-negotiable hackathon constraints

- Do not copy the reference Agentic Bug Router repository as the submission.
- Do not claim a guaranteed win.
- Do not present unmeasured prototype numbers as real results.
- Do not commit secrets/API keys/OAuth credentials.
- Do not destroy a working MVP to chase P2 features.
- Do not wait until the final hours for first integration.
- Do not make risky autonomous production actions part of the prototype.
- Do not fabricate a problem statement, organizer rule, benchmark result or source.

## Current unresolved organizer-dependent information

Status: **WAITING_FOR_PS / WAITING_FOR FINAL EVENT BRIEF**

- exact final problem statement text/ID;
- exact judging rubric/weighting if separately announced;
- exact presentation/demo time limit;
- mandatory/forbidden technologies if PS-specific;
- submission format/link requirements;
- internet/cloud restrictions if announced onsite;
- any domain-specific datasets or APIs supplied by organizers.

When any of these arrive, update this file immediately before architecture freeze.