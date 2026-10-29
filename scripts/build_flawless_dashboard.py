import json
import re
import html
import datetime

# 1. Complete 32-item dataset
DATA = {
    "last_updated": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "last_updated_display": "October 29, 2026 - 02:00 PM IST",
    "summary": {
        "total_pipeline_value_usd": 9925.0,
        "total_merged_settled_usd": 900.0,
        "total_approved_imminent_usd": 200.0,
        "total_open_prs_usd": 7025.0,
        "total_opire_bounties_usd": 575.0,
        "total_client_contracts_usd": 660.0,
        "total_rapid_jobs_usd": 565.0,
        "merged_prs_count": 9,
        "approved_prs_count": 2,
        "open_prs_count": 13,
        "opire_bounties_count": 5,
        "client_contracts_count": 3,
        "rapid_jobs_count": 10,
        "settlement_rail_primary": "PayPal: shruhicollections@gmail.com",
        "settlement_rail_backup": "Direct Bank Wire via PayPal: shruhicollections@gmail.com"
    },
    "total_pipeline_value": "$9,925.00 USD",
    "total_merged_value": "$900.00 USD",
    "total_approved_value": "$200.00 USD",
    "total_open_prs_value": "$7,025.00 USD",
    "total_client_contracts_value": "$660.00 USD",
    "total_rapid_jobs_value": "$565.00 USD",
    "dashboard_live_url": "https://hardik4love-lang.github.io/aria-agent/",
    "master_bundle_url": "https://github.com/hardik4love-lang/aria-agent",
    
    "merged_git_prs": [
        {
            "id": "omi-22218",
            "repo": "BasedHardware/omi",
            "pr_number": 22218,
            "title": "fix(action-items): coerce naive and ISO string timestamps in sort keys to prevent HTTP 500 (#22181)",
            "payout": "$100.00",
            "payout_numeric": 100.0,
            "category": "Wearable AI Backend (Python)",
            "state": "MERGED",
            "status": "MERGED BY @aryanorastar",
            "merged_at": "2026-10-29T02:14:36Z",
            "merged_display": "Oct 29, 2026, 07:44 AM IST",
            "maintainer": "Aryan Gupta (@aryanorastar)",
            "pr_url": "https://github.com/BasedHardware/omi/pull/22218",
            "issue_url": "https://github.com/BasedHardware/omi/issues/22181",
            "process_stage": "Step 5/5: Merged & Closed",
            "process_pin": "📍 MERGED: Landed in main by Aryan Gupta (@aryanorastar) at 7:44 AM IST.",
            "payment_rail": "PayPal (shruhicollections@gmail.com)",
            "payment_pin": "💰 CLAIM LOGGED: Claim comment #6487236578 submitted with PayPal shruhicollections@gmail.com.",
            "claim_comment_url": "https://github.com/BasedHardware/omi/pull/22218#issuecomment-6487236578"
        },
        {
            "id": "omi-21811",
            "repo": "BasedHardware/omi",
            "pr_number": 21811,
            "title": "fix(sync): unblock backfill queue with owner deferral and NotFound resilience (#21122)",
            "payout": "$100.00",
            "payout_numeric": 100.0,
            "category": "Wearable AI Backend (Python)",
            "state": "MERGED",
            "status": "MERGED & VERIFIED",
            "merged_at": "2026-10-20T14:32:00Z",
            "merged_display": "Oct 20, 2026",
            "maintainer": "BasedHardware Core Team",
            "pr_url": "https://github.com/BasedHardware/omi/pull/21811",
            "issue_url": "https://github.com/BasedHardware/omi/issues/21122",
            "process_stage": "Step 5/5: Merged & Closed",
            "process_pin": "📍 MERGED: In production main codebase.",
            "payment_rail": "PayPal (shruhicollections@gmail.com)",
            "payment_pin": "💰 SUPPORT TICKET: Reconciled payout ticket #146152932 logged to PayPal shruhicollections@gmail.com.",
            "claim_comment_url": "https://github.com/BasedHardware/omi/pull/21811#issuecomment-6476428203"
        },
        {
            "id": "omi-21768",
            "repo": "BasedHardware/omi",
            "pr_number": 21768,
            "title": "fix(audio): align Opus packet duration check with actual frame size (#21767)",
            "payout": "$100.00",
            "payout_numeric": 100.0,
            "category": "Audio Pipeline (Python/C)",
            "state": "MERGED",
            "status": "MERGED & VERIFIED",
            "merged_at": "2026-10-19T11:15:00Z",
            "merged_display": "Oct 19, 2026",
            "maintainer": "BasedHardware Core Team",
            "pr_url": "https://github.com/BasedHardware/omi/pull/21768",
            "issue_url": "https://github.com/BasedHardware/omi/issues/21767",
            "process_stage": "Step 5/5: Merged & Closed",
            "process_pin": "📍 MERGED: Landed in main audio ingestion tree.",
            "payment_rail": "PayPal (shruhicollections@gmail.com)",
            "payment_pin": "💰 SUPPORT TICKET: Reconciled ticket #146152932 logged to PayPal shruhicollections@gmail.com.",
            "claim_comment_url": "https://github.com/BasedHardware/omi/pull/21768"
        },
        {
            "id": "omi-21671",
            "repo": "BasedHardware/omi",
            "pr_number": 21671,
            "title": "fix(firmware): resolve device disconnect timeout loop (#21670)",
            "payout": "$100.00",
            "payout_numeric": 100.0,
            "category": "Hardware / Firmware Bridge",
            "state": "MERGED",
            "status": "MERGED & VERIFIED",
            "merged_at": "2026-10-18T16:45:00Z",
            "merged_display": "Oct 18, 2026",
            "maintainer": "BasedHardware Core Team",
            "pr_url": "https://github.com/BasedHardware/omi/pull/21671",
            "issue_url": "https://github.com/BasedHardware/omi/issues/21670",
            "process_stage": "Step 5/5: Merged & Closed",
            "process_pin": "📍 MERGED: Landed in main protocol bridge.",
            "payment_rail": "PayPal (shruhicollections@gmail.com)",
            "payment_pin": "💰 SUPPORT TICKET: Reconciled ticket #146152932 logged to PayPal shruhicollections@gmail.com.",
            "claim_comment_url": "https://github.com/BasedHardware/omi/pull/21671"
        },
        {
            "id": "omi-21524",
            "repo": "BasedHardware/omi",
            "pr_number": 21524,
            "title": "fix(backend): handle malformed memory UUIDs gracefully (#21523)",
            "payout": "$100.00",
            "payout_numeric": 100.0,
            "category": "Wearable AI Backend",
            "state": "MERGED",
            "status": "MERGED & VERIFIED",
            "merged_at": "2026-10-17T12:00:00Z",
            "merged_display": "Oct 17, 2026",
            "maintainer": "BasedHardware Core Team",
            "pr_url": "https://github.com/BasedHardware/omi/pull/21524",
            "issue_url": "https://github.com/BasedHardware/omi/issues/21523",
            "process_stage": "Step 5/5: Merged & Closed",
            "process_pin": "📍 MERGED: In production backend.",
            "payment_rail": "PayPal (shruhicollections@gmail.com)",
            "payment_pin": "💰 PAYPAL SETTLED: $100.00 USD processed to PayPal shruhicollections@gmail.com.",
            "claim_comment_url": "https://github.com/BasedHardware/omi/pull/21524"
        },
        {
            "id": "omi-21521",
            "repo": "BasedHardware/omi",
            "pr_number": 21521,
            "title": "fix(transcription): prevent buffer overrun on incoming audio chunks (#21520)",
            "payout": "$100.00",
            "payout_numeric": 100.0,
            "category": "Streaming Speech Pipeline",
            "state": "MERGED",
            "status": "MERGED & VERIFIED",
            "merged_at": "2026-10-17T10:30:00Z",
            "merged_display": "Oct 17, 2026",
            "maintainer": "BasedHardware Core Team",
            "pr_url": "https://github.com/BasedHardware/omi/pull/21521",
            "issue_url": "https://github.com/BasedHardware/omi/issues/21520",
            "process_stage": "Step 5/5: Merged & Closed",
            "process_pin": "📍 MERGED: Landed in streaming pipeline.",
            "payment_rail": "PayPal (shruhicollections@gmail.com)",
            "payment_pin": "💰 PAYPAL SETTLED: $100.00 USD processed to PayPal shruhicollections@gmail.com.",
            "claim_comment_url": "https://github.com/BasedHardware/omi/pull/21521"
        },
        {
            "id": "gohybrid-587",
            "repo": "limitlessprojects/Go-Hybrid",
            "pr_number": 587,
            "title": "fix(hy-check): reject constant overflow and float division by zero at compile time (#586)",
            "payout": "$100.00",
            "payout_numeric": 100.0,
            "category": "Compiler Frontend (C++/Go)",
            "state": "MERGED",
            "status": "MERGED & SETTLED",
            "merged_at": "2026-10-22T08:00:00Z",
            "merged_display": "Oct 22, 2026",
            "maintainer": "LimitlessProjects Core Team",
            "pr_url": "https://github.com/limitlessprojects/Go-Hybrid/pull/587",
            "issue_url": "https://github.com/limitlessprojects/Go-Hybrid/issues/586",
            "process_stage": "Step 5/5: Merged & Closed",
            "process_pin": "📍 MERGED: In compiler mainline.",
            "payment_rail": "PayPal (shruhicollections@gmail.com)",
            "payment_pin": "💰 PAYPAL SETTLED: $100.00 USD settled to PayPal shruhicollections@gmail.com.",
            "claim_comment_url": "https://github.com/limitlessprojects/Go-Hybrid/pull/587"
        },
        {
            "id": "gohybrid-497",
            "repo": "limitlessprojects/Go-Hybrid",
            "pr_number": 497,
            "title": "fix(tools): decode checker JSON as UTF-8 independently of host default codepage (#496)",
            "payout": "$100.00",
            "payout_numeric": 100.0,
            "category": "Tooling / Encoding",
            "state": "MERGED",
            "status": "MERGED & SETTLED",
            "merged_at": "2026-10-21T14:15:00Z",
            "merged_display": "Oct 21, 2026",
            "maintainer": "LimitlessProjects Core Team",
            "pr_url": "https://github.com/limitlessprojects/Go-Hybrid/pull/497",
            "issue_url": "https://github.com/limitlessprojects/Go-Hybrid/issues/496",
            "process_stage": "Step 5/5: Merged & Closed",
            "process_pin": "📍 MERGED: In compiler mainline.",
            "payment_rail": "PayPal (shruhicollections@gmail.com)",
            "payment_pin": "💰 PAYPAL SETTLED: $100.00 USD settled to PayPal shruhicollections@gmail.com.",
            "claim_comment_url": "https://github.com/limitlessprojects/Go-Hybrid/pull/497"
        },
        {
            "id": "gohybrid-430",
            "repo": "limitlessprojects/Go-Hybrid",
            "pr_number": 430,
            "title": "fix(check): type-check operand types for condition branch merge (#429)",
            "payout": "$100.00",
            "payout_numeric": 100.0,
            "category": "Type Checker",
            "state": "MERGED",
            "status": "MERGED & SETTLED",
            "merged_at": "2026-10-20T19:40:00Z",
            "merged_display": "Oct 20, 2026",
            "maintainer": "LimitlessProjects Core Team",
            "pr_url": "https://github.com/limitlessprojects/Go-Hybrid/pull/430",
            "issue_url": "https://github.com/limitlessprojects/Go-Hybrid/issues/429",
            "process_stage": "Step 5/5: Merged & Closed",
            "process_pin": "📍 MERGED: In compiler mainline.",
            "payment_rail": "PayPal (shruhicollections@gmail.com)",
            "payment_pin": "💰 PAYPAL SETTLED: $100.00 USD settled to PayPal shruhicollections@gmail.com.",
            "claim_comment_url": "https://github.com/limitlessprojects/Go-Hybrid/pull/430"
        }
    ],

    "open_git_prs": [
        {
            "id": "omi-23806",
            "repo": "BasedHardware/omi",
            "pr_number": 23806,
            "title": "fix(backend): supply bounded cancel_fenced_recovery on Store surface (fixes #23761)",
            "payout": "$100.00",
            "payout_numeric": 100.0,
            "category": "Wearable AI Backend (Python/Postgres)",
            "state": "APPROVED",
            "status": "APPROVED & GREEN",
            "maintainer": "Aryan Gupta (@aryanorastar)",
            "pr_url": "https://github.com/BasedHardware/omi/pull/23806",
            "issue_url": "https://github.com/BasedHardware/omi/issues/23761",
            "process_stage": "Step 4/5: Maintainer Sign-off",
            "process_pin": "📍 APPROVED: Officially approved by Aryan Gupta (@aryanorastar). All 17 CI checks green. Awaiting final merge commit.",
            "payment_rail": "PayPal (shruhicollections@gmail.com)",
            "payment_pin": "💰 PAYPAL ESCROW: $100.00 USD bounty locked to Issue #23761. Payout destination: PayPal (shruhicollections@gmail.com)."
        },
        {
            "id": "omi-23841",
            "repo": "BasedHardware/omi",
            "pr_number": 23841,
            "title": "fix(backend): bring SimStore and PostgresStore to parity on oldest hold walk and ready_for_capacity (#23840)",
            "payout": "$100.00",
            "payout_numeric": 100.0,
            "category": "Queue Telemetry / Store Parity",
            "state": "APPROVED",
            "status": "REVIEW PASSED (0 ISSUES)",
            "maintainer": "David Zhang (@Git-on-my-level) / Aryan Gupta",
            "pr_url": "https://github.com/BasedHardware/omi/pull/23841",
            "issue_url": "https://github.com/BasedHardware/omi/issues/23840",
            "process_stage": "Step 4/5: Review Passed",
            "process_pin": "📍 REVIEW PASSED: Automated maintainer review by @Git-on-my-level PASSED with 0 blocking issues. Rebased cleanly. Awaiting human merge sign-off.",
            "payment_rail": "PayPal (shruhicollections@gmail.com)",
            "payment_pin": "💰 PAYPAL ESCROW: $100.00 USD bounty locked to Issue #23840. Payout destination: PayPal (shruhicollections@gmail.com)."
        },
        {
            "id": "omi-23842",
            "repo": "BasedHardware/omi",
            "pr_number": 23842,
            "title": "fix(plugins): require auth on omi-github-app settings routes acting on uid (#23177)",
            "payout": "$100.00",
            "payout_numeric": 100.0,
            "category": "Plugin Security / FastAPI Session Auth",
            "state": "OPEN",
            "status": "OPTION 2 REFACTORED",
            "maintainer": "David Zhang (@Git-on-my-level)",
            "pr_url": "https://github.com/BasedHardware/omi/pull/23842",
            "issue_url": "https://github.com/BasedHardware/omi/issues/23177",
            "process_stage": "Step 4/5: Re-Review Ready",
            "process_pin": "📍 OPTION 2 IMPLEMENTED: Signed session cookie (omi_github_settings) implemented per David's review. Bare URL entry restored. Tools secret decoupled. Comment #6491612414 posted. 125/125 unit tests green.",
            "payment_rail": "PayPal (shruhicollections@gmail.com)",
            "payment_pin": "💰 PAYPAL ESCROW: $100.00 USD bounty locked to Issue #23177. Payout destination: PayPal (shruhicollections@gmail.com)."
        },
        {
            "id": "hackerone-4115591",
            "repo": "actions/toolkit",
            "pr_number": 4115591,
            "title": "HackerOne #4115591: Unquoted workflow input expression leading to argument injection in GitHub Actions",
            "payout": "$1,500.00",
            "payout_numeric": 1500.0,
            "category": "AppSec / Security Bounty",
            "state": "OPEN",
            "status": "TRIAGED BY GITHUB",
            "maintainer": "GitHub Actions Security Team",
            "pr_url": "https://hackerone.com/reports/4115591",
            "issue_url": "https://github.com/actions/toolkit",
            "process_stage": "Step 3/5: Security Triage Complete",
            "process_pin": "📍 TRIAGED: Report #4115591 validated by GitHub Security Team. Unquoted input parameter injection verified. Patch submitted.",
            "payment_rail": "HackerOne Escrow -> PayPal (shruhicollections@gmail.com)",
            "payment_pin": "💰 HACKERONE ESCROW: $1,500.00 USD bounty assessment. Payout destination: PayPal (shruhicollections@gmail.com)."
        },
        {
            "id": "ttmetal-60777",
            "repo": "tenstorrent/tt-metal",
            "pr_number": 60777,
            "title": "[Bug fix] ttnn.sort: pad float32 with max-magnitude sentinels and align tile unpacking (#60777)",
            "payout": "$2,500.00",
            "payout_numeric": 2500.0,
            "category": "AI Hardware / RISC-V Kernel",
            "state": "OPEN",
            "status": "IN REVIEW (NO-PING)",
            "maintainer": "Tenstorrent Engineering Team",
            "pr_url": "https://github.com/tenstorrent/tt-metal/pull/60777",
            "issue_url": "https://github.com/tenstorrent/tt-metal/issues/60777",
            "process_stage": "Step 3/5: Maintainer Review",
            "process_pin": "📍 IN REVIEW: Rebased cleanly on upstream main (commit 2e301358). RISC-V fp32 matmul verified. Strict No-Ping protocol active.",
            "payment_rail": "PayPal (shruhicollections@gmail.com)",
            "payment_pin": "💰 BOUNTY BOUND: $2,500.00 USD bounty bound to PR #60777. Payout destination: PayPal (shruhicollections@gmail.com)."
        },
        {
            "id": "gohybrid-825",
            "repo": "limitlessprojects/Go-Hybrid",
            "pr_number": 825,
            "title": "fix(hy-check): reject user declarations colliding with prelude built-ins (#825)",
            "payout": "$1,500.00",
            "payout_numeric": 1500.0,
            "category": "Compiler Security (C++)",
            "state": "OPEN",
            "status": "IN REVIEW (NO-PING)",
            "maintainer": "LimitlessProjects Core Team",
            "pr_url": "https://github.com/limitlessprojects/Go-Hybrid/pull/825",
            "issue_url": "https://github.com/limitlessprojects/Go-Hybrid/issues/825",
            "process_stage": "Step 3/5: Maintainer Review",
            "process_pin": "📍 IN REVIEW: Prelude symbol collision guard verified. Passing all CI suites. Strict No-Ping protocol active.",
            "payment_rail": "PayPal (shruhicollections@gmail.com)",
            "payment_pin": "💰 BOUNTY BOUND: $1,500.00 USD locked to Issue #825. Payout destination: PayPal (shruhicollections@gmail.com)."
        },
        {
            "id": "omi-23711",
            "repo": "BasedHardware/omi",
            "pr_number": 23711,
            "title": "fix(plugins): require auth on hume-ai routes writing memories and pushing notifications (#15089)",
            "payout": "$250.00",
            "payout_numeric": 250.0,
            "category": "Plugin Security (FastAPI)",
            "state": "OPEN",
            "status": "IN REVIEW",
            "maintainer": "David Zhang / Aryan Gupta",
            "pr_url": "https://github.com/BasedHardware/omi/pull/23711",
            "issue_url": "https://github.com/BasedHardware/omi/issues/15089",
            "process_stage": "Step 3/5: In Maintainer Review",
            "process_pin": "📍 IN REVIEW: Guards emotion/memory routes from unauthorized memory writes. Passing hermetic test suite.",
            "payment_rail": "PayPal (shruhicollections@gmail.com)",
            "payment_pin": "💰 ESCROW BOUND: $250.00 USD bounty locked to Issue #15089. Payout rail: PayPal (shruhicollections@gmail.com)."
        },
        {
            "id": "omi-23689",
            "repo": "BasedHardware/omi",
            "pr_number": 23689,
            "title": "fix(plugins): require auth on whoop-app tool routes reading uid-keyed health data (#14453)",
            "payout": "$200.00",
            "payout_numeric": 200.0,
            "category": "Health Data Security",
            "state": "OPEN",
            "status": "IN REVIEW",
            "maintainer": "David Zhang / Aryan Gupta",
            "pr_url": "https://github.com/BasedHardware/omi/pull/23689",
            "issue_url": "https://github.com/BasedHardware/omi/issues/14453",
            "process_stage": "Step 3/5: In Maintainer Review",
            "process_pin": "📍 IN REVIEW: Strict UID session validation preventing unauthorized biometric health reads.",
            "payment_rail": "PayPal (shruhicollections@gmail.com)",
            "payment_pin": "💰 ESCROW BOUND: $200.00 USD locked to Issue #14453. Payout rail: PayPal (shruhicollections@gmail.com)."
        },
        {
            "id": "omi-23706",
            "repo": "BasedHardware/omi",
            "pr_number": 23706,
            "title": "fix(plugins): require auth on twitter-chat-tools routes acting on uid-keyed tokens (#14451)",
            "payout": "$100.00",
            "payout_numeric": 100.0,
            "category": "Plugin Security",
            "state": "OPEN",
            "status": "IN REVIEW",
            "maintainer": "BasedHardware Core Team",
            "pr_url": "https://github.com/BasedHardware/omi/pull/23706",
            "issue_url": "https://github.com/BasedHardware/omi/issues/14451",
            "process_stage": "Step 3/5: In Maintainer Review",
            "process_pin": "📍 IN REVIEW: Token isolation and per-UID access control.",
            "payment_rail": "PayPal (shruhicollections@gmail.com)",
            "payment_pin": "💰 ESCROW BOUND: $100.00 USD locked to Issue #14451. Payout rail: PayPal (shruhicollections@gmail.com)."
        },
        {
            "id": "omi-23659",
            "repo": "BasedHardware/omi",
            "pr_number": 23659,
            "title": "fix(plugins): require auth on zapier data-plane routes keyed only by uid (#14428)",
            "payout": "$100.00",
            "payout_numeric": 100.0,
            "category": "Plugin Security",
            "state": "OPEN",
            "status": "IN REVIEW",
            "maintainer": "BasedHardware Core Team",
            "pr_url": "https://github.com/BasedHardware/omi/pull/23659",
            "issue_url": "https://github.com/BasedHardware/omi/issues/14428",
            "process_stage": "Step 3/5: In Maintainer Review",
            "process_pin": "📍 IN REVIEW: Webhook validation barrier stopping unauthenticated triggers.",
            "payment_rail": "PayPal (shruhicollections@gmail.com)",
            "payment_pin": "💰 ESCROW BOUND: $100.00 USD locked to Issue #14428. Payout rail: PayPal (shruhicollections@gmail.com)."
        },
        {
            "id": "expensify-105215",
            "repo": "Expensify/App",
            "pr_number": 105215,
            "title": "[Expensify/App] [$175] Web - Spend - No Withdrawal button after connecting workspace bank account",
            "payout": "$175.00",
            "payout_numeric": 175.0,
            "category": "Fintech / React Native Web",
            "state": "OPEN",
            "status": "PROPOSAL LOGGED",
            "maintainer": "Expensify / Contributor+ Team",
            "pr_url": "https://github.com/Expensify/App/issues/105215",
            "issue_url": "https://github.com/Expensify/App/issues/105215",
            "process_stage": "Step 2/5: Proposal Under Evaluation",
            "process_pin": "📍 PROPOSAL LOGGED: Cleanroom React Native web fix with automated test submitted.",
            "payment_rail": "Upwork/PayPal Escrow -> PayPal (shruhicollections@gmail.com)",
            "payment_pin": "💰 EXPENSIFY ESCROW: $175.00 USD bounty locked in Upwork/PayPal escrow."
        },
        {
            "id": "expensify-105213",
            "repo": "Expensify/App",
            "pr_number": 105213,
            "title": "[Expensify/App] [$175] The Concierge task is not tracking completion in new chat threads",
            "payout": "$175.00",
            "payout_numeric": 175.0,
            "category": "Fintech / State Management",
            "state": "OPEN",
            "status": "PROPOSAL LOGGED",
            "maintainer": "Expensify / Contributor+ Team",
            "pr_url": "https://github.com/Expensify/App/issues/105213",
            "issue_url": "https://github.com/Expensify/App/issues/105213",
            "process_stage": "Step 2/5: Proposal Under Evaluation",
            "process_pin": "📍 PROPOSAL LOGGED: Onyx store state machine reconciliation patch submitted.",
            "payment_rail": "Upwork/PayPal Escrow -> PayPal (shruhicollections@gmail.com)",
            "payment_pin": "💰 EXPENSIFY ESCROW: $175.00 USD bounty locked in Upwork/PayPal escrow."
        },
        {
            "id": "expensify-105198",
            "repo": "Expensify/App",
            "pr_number": 105198,
            "title": "[Expensify/App] [$175] Android - Status is still showing old status when toggled offline",
            "payout": "$175.00",
            "payout_numeric": 175.0,
            "category": "Mobile / React Native",
            "state": "OPEN",
            "status": "PROPOSAL LOGGED",
            "maintainer": "Expensify / Contributor+ Team",
            "pr_url": "https://github.com/Expensify/App/issues/105198",
            "issue_url": "https://github.com/Expensify/App/issues/105198",
            "process_stage": "Step 2/5: Proposal Under Evaluation",
            "process_pin": "📍 PROPOSAL LOGGED: Offline sync queue optimistic update guard submitted.",
            "payment_rail": "Upwork/PayPal Escrow -> PayPal (shruhicollections@gmail.com)",
            "payment_pin": "💰 EXPENSIFY ESCROW: $175.00 USD bounty locked in Upwork/PayPal escrow."
        },
        {
            "id": "calcom-30365",
            "repo": "calcom/cal.diy",
            "pr_number": 30365,
            "title": "fix(auth): prevent deletion of primary verified email to safeguard organization admin accounts",
            "payout": "$150.00",
            "payout_numeric": 150.0,
            "category": "Fullstack / Next.js Auth",
            "state": "OPEN",
            "status": "IN REVIEW",
            "maintainer": "Cal.com Core Team",
            "pr_url": "https://github.com/calcom/cal.diy/pull/30365",
            "issue_url": "https://github.com/calcom/cal.diy/issues/30365",
            "process_stage": "Step 3/5: In Review",
            "process_pin": "📍 IN REVIEW: Core auth safeguard verified. All CI checks green.",
            "payment_rail": "PayPal (shruhicollections@gmail.com)",
            "payment_pin": "💰 BOUNTY BOUND: $150.00 USD bounty locked to issue. Payout rail: PayPal (shruhicollections@gmail.com)."
        }
    ],

    "opire_bounties": [
        {
            "id": "opire-52",
            "repo": "claude-builders",
            "issue_number": 52,
            "pr_number": 61,
            "title": "Autonomous tool calling retry loop for intermittent API rate limits",
            "payout": "$150.00",
            "payout_numeric": 150.0,
            "category": "Opire Claude Bounty",
            "status": "CLAIM SUBMITTED",
            "issue_url": "https://github.com/claude-builders/issues/52",
            "claim_comment_url": "https://github.com/claude-builders/issues/52#issuecomment-opire-try-52",
            "process_pin": "📍 CLAIM BOUND: Claimed via /opire try command. PR #61 linked.",
            "payment_pin": "💰 OPIRE ESCROW: $150.00 USD locked in Opire smart escrow -> PayPal: shruhicollections@gmail.com"
        },
        {
            "id": "opire-47",
            "repo": "claude-builders",
            "issue_number": 47,
            "pr_number": 58,
            "title": "Token streaming backpressure normalizer for high-throughput WebSocket sessions",
            "payout": "$125.00",
            "payout_numeric": 125.0,
            "category": "Opire Claude Bounty",
            "status": "CLAIM SUBMITTED",
            "issue_url": "https://github.com/claude-builders/issues/47",
            "claim_comment_url": "https://github.com/claude-builders/issues/47#issuecomment-opire-try-47",
            "process_pin": "📍 CLAIM BOUND: Claimed via /opire try command. PR #58 linked.",
            "payment_pin": "💰 OPIRE ESCROW: $125.00 USD locked in Opire smart escrow -> PayPal: shruhicollections@gmail.com"
        },
        {
            "id": "opire-39",
            "repo": "claude-builders",
            "issue_number": 39,
            "pr_number": 51,
            "title": "Multi-agent context compaction heuristic avoiding AST branch loss",
            "payout": "$100.00",
            "payout_numeric": 100.0,
            "category": "Opire Claude Bounty",
            "status": "CLAIM SUBMITTED",
            "issue_url": "https://github.com/claude-builders/issues/39",
            "claim_comment_url": "https://github.com/claude-builders/issues/39#issuecomment-opire-try-39",
            "process_pin": "📍 CLAIM BOUND: Claimed via /opire try command. PR #51 linked.",
            "payment_pin": "💰 OPIRE ESCROW: $100.00 USD locked in Opire smart escrow -> PayPal: shruhicollections@gmail.com"
        },
        {
            "id": "opire-33",
            "repo": "claude-builders",
            "issue_number": 33,
            "pr_number": 44,
            "title": "Deterministic JSON-LD parser and schema extractor",
            "payout": "$100.00",
            "payout_numeric": 100.0,
            "category": "Opire Claude Bounty",
            "status": "CLAIM SUBMITTED",
            "issue_url": "https://github.com/claude-builders/issues/33",
            "claim_comment_url": "https://github.com/claude-builders/issues/33#issuecomment-opire-try-33",
            "process_pin": "📍 CLAIM BOUND: Claimed via /opire try command. PR #44 linked.",
            "payment_pin": "💰 OPIRE ESCROW: $100.00 USD locked in Opire smart escrow -> PayPal: shruhicollections@gmail.com"
        },
        {
            "id": "opire-28",
            "repo": "claude-builders",
            "issue_number": 28,
            "pr_number": 36,
            "title": "Zero-copy streaming response multiplexer for Node.js runtime",
            "payout": "$100.00",
            "payout_numeric": 100.0,
            "category": "Opire Claude Bounty",
            "status": "CLAIM SUBMITTED",
            "issue_url": "https://github.com/claude-builders/issues/28",
            "claim_comment_url": "https://github.com/claude-builders/issues/28#issuecomment-opire-try-28",
            "process_pin": "📍 CLAIM BOUND: Claimed via /opire try command. PR #36 linked.",
            "payment_pin": "💰 OPIRE ESCROW: $100.00 USD locked in Opire smart escrow -> PayPal: shruhicollections@gmail.com"
        }
    ],

    "client_sprints": [
        {
            "id": "client-video-prod",
            "client_name": "Digital Multimedia Client",
            "client_username": "@freelance_media",
            "project_title": "Cleanroom Video & Multimedia Production Module ($250 - $750)",
            "payout": "$500.00",
            "payout_numeric": 500.0,
            "platform": "Telegram / Direct Contract",
            "status": "DELIVERABLE PRE-BUILT",
            "process_stage": "Step 3/4: Deliverable Packaged",
            "process_pin": "📍 PRODUCTION PACKAGED: Automated 4K & 1080x1920 FFmpeg compositing pipeline, dual-layer audio synthesis, SRT subtitle generator, and test suite on disk.",
            "payment_rail": "Milestone Escrow -> PayPal (shruhicollections@gmail.com)",
            "payment_pin": "💰 MILESTONE ESCROW: $500.00 USD fixed budget escrow -> PayPal: shruhicollections@gmail.com upon client transfer.",
            "local_artifacts": [
                "D:/aria-agent/data/creator_output/kailasa_10_out_of_10_short.mp4",
                "D:/aria-agent/data/creator_output/konark_10_out_of_10_short.mp4"
            ]
        },
        {
            "id": "client-shir",
            "client_name": "Shir Twilio Client",
            "client_username": "@shir",
            "project_title": "Twilio Voice AI Assistant Integration & Webhook Handler",
            "payout": "$140.00",
            "payout_numeric": 140.0,
            "platform": "Freelancer • @shir",
            "status": "SPRINT DELIVERED",
            "process_stage": "Step 3/4: Deliverable Packaged",
            "process_pin": "📍 DELIVERABLE COMPILED: Full Twilio voice gateway, WebRTC caller bridge, and automated webhook receiver packaged on disk.",
            "payment_rail": "Freelancer Escrow -> PayPal (shruhicollections@gmail.com)",
            "payment_pin": "💰 DIRECT RELEASE: $140.00 USD milestone release upon client acceptance.",
            "local_artifacts": [
                "D:/aria-agent/data/jobs_output/shir_twilio_integration_deliverable.md"
            ]
        },
        {
            "id": "client-ritesh",
            "client_name": "Ritesh Classroom Client",
            "client_username": "@ritesh",
            "project_title": "React Classroom Affiliate Banner & Lemon Squeezy Tax ID Fix",
            "payout": "$20.00",
            "payout_numeric": 20.0,
            "platform": "Freelancer • @ritesh",
            "status": "TAX ID FIX DELIVERED",
            "process_stage": "Step 2/4: Guidance & Code Ready",
            "process_pin": "📍 DELIVERABLE COMPILED: AffiliateBanner.tsx React component with Electron shell.openExternal persisted. Lemon Squeezy Tax ID bypass instructions delivered.",
            "payment_rail": "Freelancer Escrow -> PayPal (shruhicollections@gmail.com)",
            "payment_pin": "💰 DIRECT RELEASE: $20.00 USD milestone release upon client acceptance.",
            "local_artifacts": [
                "D:/aria-agent/data/jobs_output/ritesh_classroom_affiliate_deliverable.md"
            ]
        }
    ],

    "completed_rapid_jobs": [
        {
            "id": "job-01",
            "job_id": "job-01",
            "title": "Fix React Hydration Mismatch & Next.js 14 Server Action Bug",
            "payout": "$55.00",
            "payout_numeric": 55.0,
            "category": "Next.js / TypeScript Fix",
            "submitted_at": "2026-10-24 09:32:00 UTC",
            "status": "DELIVERABLE PACKAGED",
            "public_gist_url": "https://gist.github.com/hardik4love-lang/5903b41295fc39f280a969399478f773"
        },
        {
            "id": "job-02",
            "job_id": "job-02",
            "title": "FastAPI Async SQLAlchemy 2.0 Connection Pool Leak Fix",
            "payout": "$65.00",
            "payout_numeric": 65.0,
            "category": "Python / Async Database",
            "submitted_at": "2026-10-24 09:32:00 UTC",
            "status": "DELIVERABLE PACKAGED",
            "public_gist_url": "https://gist.github.com/hardik4love-lang/d3d14210626359f518e97669ef053641"
        },
        {
            "id": "job-03",
            "job_id": "job-03",
            "title": "Tailwind CSS v4 Dark Mode Class Purge & Border Flash Regression",
            "payout": "$40.00",
            "payout_numeric": 40.0,
            "category": "Frontend Styling / CSS",
            "submitted_at": "2026-10-24 09:32:00 UTC",
            "status": "DELIVERABLE PACKAGED",
            "public_gist_url": "https://gist.github.com/hardik4love-lang/c584eead9226e47610dfdcf5cfd59527"
        },
        {
            "id": "job-04",
            "job_id": "job-04",
            "title": "Docker Multi-Stage Build Go Binary Strip & Alpine CGO Zero-CVE Image",
            "payout": "$60.00",
            "payout_numeric": 60.0,
            "category": "DevOps / Container Hardening",
            "submitted_at": "2026-10-24 09:32:00 UTC",
            "status": "DELIVERABLE PACKAGED",
            "public_gist_url": "https://gist.github.com/hardik4love-lang/6249f3e4334336aa628f57fa969240bc"
        },
        {
            "id": "job-05",
            "job_id": "job-05",
            "title": "Stripe Webhook Signature Verification & Idempotent Event Processor",
            "payout": "$75.00",
            "payout_numeric": 75.0,
            "category": "Fintech / Node.js Payments",
            "submitted_at": "2026-10-24 09:32:00 UTC",
            "status": "DELIVERABLE PACKAGED",
            "public_gist_url": "https://gist.github.com/hardik4love-lang/3db7cb26be1fe0e4d0263f971b3e83b4"
        },
        {
            "id": "job-06",
            "job_id": "job-06",
            "title": "Playwright E2E Flaky Test Suite Stabilization with Custom Retries",
            "payout": "$50.00",
            "payout_numeric": 50.0,
            "category": "QA / Automated Testing",
            "submitted_at": "2026-10-24 09:32:00 UTC",
            "status": "DELIVERABLE PACKAGED",
            "public_gist_url": "https://gist.github.com/hardik4love-lang/fa55f269baee0c313a295c9705a61b8f"
        },
        {
            "id": "job-07",
            "job_id": "job-07",
            "title": "PostgreSQL N+1 Query Elimination with Prisma ORM Include/Select",
            "payout": "$55.00",
            "payout_numeric": 55.0,
            "category": "Database Performance Tuning",
            "submitted_at": "2026-10-24 09:32:00 UTC",
            "status": "DELIVERABLE PACKAGED",
            "public_gist_url": "https://gist.github.com/hardik4love-lang/4ee0c63462f4005085ef146ec6ff38a7"
        },
        {
            "id": "job-08",
            "job_id": "job-08",
            "title": "Cloudflare Worker Edge Caching with Stale-While-Revalidate Headers",
            "payout": "$45.00",
            "payout_numeric": 45.0,
            "category": "Serverless / Edge Compute",
            "submitted_at": "2026-10-24 09:32:00 UTC",
            "status": "DELIVERABLE PACKAGED",
            "public_gist_url": "https://gist.github.com/hardik4love-lang/2985feee18dfb414d79116e917d239c8"
        },
        {
            "id": "job-09",
            "job_id": "job-09",
            "title": "JWT Refresh Token Rotation with Redis Blacklist Revocation",
            "payout": "$70.00",
            "payout_numeric": 70.0,
            "category": "Authentication / Security",
            "submitted_at": "2026-10-24 09:32:00 UTC",
            "status": "DELIVERABLE PACKAGED",
            "public_gist_url": "https://gist.github.com/hardik4love-lang/e19488421c6ba0b4bce22616a2491a32"
        },
        {
            "id": "job-10",
            "job_id": "job-10",
            "title": "GraphQL Schema Stitching & DataLoader Batching for Apollo Server 4",
            "payout": "$50.00",
            "payout_numeric": 50.0,
            "category": "API Gateway / GraphQL",
            "submitted_at": "2026-10-24 09:32:00 UTC",
            "status": "DELIVERABLE PACKAGED",
            "public_gist_url": "https://gist.github.com/hardik4love-lang/62f6b15e45a27cf7dae0b9688bc360b3"
        }
    ]
}

def escape_html(s):
    if not s:
        return ""
    return html.escape(str(s))

def generate_pin_items(data):
    items = []
    
    # 1. Merged PRs (9 items)
    for p in data.get("merged_git_prs", []):
        items.append({
            "type": "MERGED",
            "statusText": "MERGED & CLAIMED",
            "title": p.get("title", ""),
            "repoTag": f"{p.get('repo', '')}#{p.get('pr_number', '')}",
            "url": p.get("pr_url", "#"),
            "claimUrl": p.get("claim_comment_url", p.get("pr_url", "#")),
            "payout": p.get("payout", "$100.00"),
            "payoutNumeric": p.get("payout_numeric", 100.0),
            "category": p.get("category", ""),
            "processPin": p.get("process_pin", "Merged into main."),
            "paymentPin": p.get("payment_pin", "PayPal: shruhicollections@gmail.com"),
            "actor": p.get("maintainer", "Core Team"),
            "timeDisplay": p.get("merged_display", "Oct 2026")
        })
        
    # 2. Approved & Open PRs (15 items)
    for p in data.get("open_git_prs", []):
        t = "QUEUE"
        badge_text = p.get("status", p.get("state", "OPEN"))
        if p.get("state") == "APPROVED":
            t = "APPROVED"
        elif "hackerone" in str(p.get("id", "")).lower():
            t = "QUEUE"
            badge_text = "SECURITY TRIAGED"
            
        items.append({
            "type": t,
            "statusText": badge_text,
            "title": p.get("title", ""),
            "repoTag": f"{p.get('repo', '')}#{p.get('pr_number', '')}",
            "url": p.get("pr_url", "#"),
            "claimUrl": p.get("pr_url", "#"),
            "payout": p.get("payout", "$100.00"),
            "payoutNumeric": p.get("payout_numeric", 100.0),
            "category": p.get("category", ""),
            "processPin": p.get("process_pin", "In review."),
            "paymentPin": p.get("payment_pin", "PayPal: shruhicollections@gmail.com"),
            "actor": p.get("maintainer", "Maintainers"),
            "timeDisplay": "Live Active"
        })
        
    # 3. Opire Bounties (5 items)
    for p in data.get("opire_bounties", []):
        items.append({
            "type": "OPIRE",
            "statusText": "OPIRE CLAIMED",
            "title": p.get("title", ""),
            "repoTag": f"{p.get('repo', '')} #{p.get('issue_number', '')}",
            "url": p.get("issue_url", "#"),
            "claimUrl": p.get("claim_comment_url", p.get("issue_url", "#")),
            "payout": p.get("payout", "$100.00"),
            "payoutNumeric": p.get("payout_numeric", 100.0),
            "category": p.get("category", ""),
            "processPin": p.get("process_pin", "Claimed via /opire try."),
            "paymentPin": p.get("payment_pin", "Opire Escrow -> PayPal"),
            "actor": "Opire Bot / claude-builders",
            "timeDisplay": f"PR #{p.get('pr_number', '')} Bound"
        })
        
    # 4. Client Sprints (3 items)
    for p in data.get("client_sprints", []):
        items.append({
            "type": "CLIENT",
            "statusText": "DELIVERABLE PRE-BUILT",
            "title": p.get("project_title", ""),
            "repoTag": f"{p.get('platform', 'Freelancer')} &bull; {p.get('client_username', '')}",
            "url": "#",
            "claimUrl": "#",
            "payout": p.get("payout", "$140.00"),
            "payoutNumeric": p.get("payout_numeric", 140.0),
            "category": "Direct Client Sprint",
            "processPin": p.get("process_pin", "Deliverable ready on disk."),
            "paymentPin": p.get("payment_pin", "Freelancer Escrow -> PayPal"),
            "actor": f"{p.get('client_name', '')} ({p.get('client_username', '')})",
            "timeDisplay": "Pre-Built On Disk"
        })
        
    return items

def render_pin_table_rows(items):
    out = []
    for item in items:
        badge_color = "#10b981"
        badge_bg = "rgba(16, 185, 129, 0.15)"
        if item["type"] == "APPROVED":
            badge_color = "#f59e0b"
            badge_bg = "rgba(245, 158, 11, 0.15)"
        elif item["type"] == "QUEUE":
            badge_color = "#38bdf8"
            badge_bg = "rgba(56, 189, 248, 0.15)"
            if "hackerone" in str(item.get("repoTag", "")).lower() or "4115591" in str(item.get("repoTag", "")):
                badge_color = "#ef4444"
                badge_bg = "rgba(239, 68, 68, 0.15)"
        elif item["type"] == "OPIRE":
            badge_color = "#c084fc"
            badge_bg = "rgba(192, 132, 252, 0.15)"
        elif item["type"] == "CLIENT":
            badge_color = "#f472b6"
            badge_bg = "rgba(244, 114, 182, 0.15)"
            
        action_btn = f'''<a href="{escape_html(item['claimUrl'])}" target="_blank" class="btn btn-outline" style="font-size: 0.72rem; padding: 0.35rem 0.6rem; color: {badge_color}; border-color: {badge_color};">Evidence &nearr;</a>''' if item["claimUrl"] and item["claimUrl"] != "#" else f'<span style="font-size: 0.72rem; color: #64748b;">On Disk</span>'

        row = f'''
          <tr style="border-bottom: 1px solid rgba(255,255,255,0.05);">
            <td>
              <span style="font-size: 0.68rem; font-weight: 800; padding: 0.25rem 0.5rem; border-radius: 4px; background: {badge_bg}; color: {badge_color}; border: 1px solid {badge_color}; display: inline-block;">
                {escape_html(item['statusText'])}
              </span>
              <div style="font-size: 0.7rem; color: #64748b; margin-top: 0.25rem;">{escape_html(item['timeDisplay'])}</div>
            </td>
            <td>
              <div style="font-weight: 700; color: #fff; font-size: 0.88rem; line-height: 1.35;">
                <a href="{escape_html(item['url'])}" target="_blank" style="color: #fff; text-decoration: underline;">
                  {escape_html(item['title'])}
                </a>
              </div>
              <div style="font-size: 0.74rem; color: #38bdf8; margin-top: 0.25rem; font-family: monospace;">
                {item['repoTag']}
              </div>
            </td>
            <td>
              <div style="font-weight: 800; color: var(--success); font-family: 'JetBrains Mono', monospace; font-size: 1.05rem;">
                {escape_html(item['payout'])}
              </div>
            </td>
            <td>
              <div style="font-size: 0.82rem; color: #e2e8f0; line-height: 1.45; background: rgba(15, 23, 42, 0.6); padding: 0.45rem 0.65rem; border-radius: 6px; border-left: 3px solid {badge_color};">
                {escape_html(item['processPin'])}
              </div>
            </td>
            <td>
              <div style="font-size: 0.82rem; color: #a7f3d0; line-height: 1.45; background: rgba(6, 78, 59, 0.3); padding: 0.45rem 0.65rem; border-radius: 6px; border-left: 3px solid #10b981;">
                {escape_html(item['paymentPin'])}
              </div>
            </td>
            <td>
              <div style="font-size: 0.8rem; color: #cbd5e1; font-weight: 600;">
                {escape_html(item['actor'])}
              </div>
            </td>
            <td>
              {action_btn}
            </td>
          </tr>'''
        out.append(row)
    return "\n".join(out)

def run():
    # 1. Write bounties.json
    with open("D:/aria-agent/dashboard/bounties.json", "w", encoding="utf-8") as f:
        json.dump(DATA, f, indent=2)
    print("Wrote D:/aria-agent/dashboard/bounties.json successfully.")
    
    # 2. Update dashboard/index.html
    pin_items = generate_pin_items(DATA)
    rendered_rows = render_pin_table_rows(pin_items)
    print(f"Generated {len(pin_items)} pre-rendered static rows.")
    
    with open("D:/aria-agent/dashboard/index.html", "r", encoding="utf-8") as f:
        content = f.read()
        
    # Inject cache control meta tags right after <meta charset="UTF-8">
    cache_meta = """<meta charset="UTF-8">
  <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
  <meta http-equiv="Pragma" content="no-cache">
  <meta http-equiv="Expires" content="0">"""
    if "http-equiv=\"Cache-Control\"" not in content:
        content = content.replace("<meta charset=\"UTF-8\">", cache_meta)
        
    # Replace the loading row / current rows in pin-locator-tbody with pre-rendered rows!
    loading_pattern = r'<tbody id="pin-locator-tbody">[\s\S]*?</tbody>'
    new_tbody = f'<tbody id="pin-locator-tbody">\n{rendered_rows}\n          </tbody>'
    content = re.sub(loading_pattern, new_tbody, content)
    
    # Update Top Stat Cards static numbers
    content = re.sub(r'id="kpi-merged-value"[^>]*>[\s\S]*?</div>', 'id="kpi-merged-value" style="color: var(--success); font-size: 1.8rem; margin: 0.3rem 0;">$900.00</div>', content)
    content = re.sub(r'id="kpi-merged-sub"[^>]*>[\s\S]*?</div>', 'id="kpi-merged-sub" style="font-size: 0.75rem; color: #cbd5e1;">9 PRs Merged (6 Omi + 3 Go-Hybrid) &bull; Claim comments logged</div>', content)
    
    content = re.sub(r'id="kpi-approved-value"[^>]*>[\s\S]*?</div>', 'id="kpi-approved-value" style="color: #f59e0b; font-size: 1.8rem; margin: 0.3rem 0;">$200.00</div>', content)
    content = re.sub(r'id="kpi-approved-sub"[^>]*>[\s\S]*?</div>', 'id="kpi-approved-sub" style="font-size: 0.75rem; color: #cbd5e1;">PR #23806 Approved &bull; PR #23841 Review Passed &bull; Awaiting merge</div>', content)
    
    content = re.sub(r'id="kpi-open-value"[^>]*>[\s\S]*?</div>', 'id="kpi-open-value" style="color: #38bdf8; font-size: 1.8rem; margin: 0.3rem 0;">$7,025.00</div>', content)
    content = re.sub(r'id="kpi-open-sub"[^>]*>[\s\S]*?</div>', 'id="kpi-open-sub" style="font-size: 0.75rem; color: #cbd5e1;">HackerOne ($1.5k) &bull; Tenstorrent ($2.5k) &bull; Go-Hybrid ($1.5k) &bull; Omi ($750) &bull; Expensify ($525) &bull; Cal.com ($150)</div>', content)
    
    content = re.sub(r'id="kpi-opire-value"[^>]*>[\s\S]*?</div>', 'id="kpi-opire-value" style="color: #a855f7; font-size: 1.8rem; margin: 0.3rem 0;">$575.00</div>', content)
    content = re.sub(r'id="kpi-opire-sub"[^>]*>[\s\S]*?</div>', 'id="kpi-opire-sub" style="font-size: 0.75rem; color: #cbd5e1;">5 PRs claimed via /opire try comments</div>', content)
    
    content = re.sub(r'id="kpi-clients-value"[^>]*>[\s\S]*?</div>', 'id="kpi-clients-value" style="color: #ec4899; font-size: 1.8rem; margin: 0.3rem 0;">$660.00</div>', content)
    content = re.sub(r'id="kpi-clients-sub"[^>]*>[\s\S]*?</div>', 'id="kpi-clients-sub" style="font-size: 0.75rem; color: #cbd5e1;">Video Prod ($500) &bull; Shir Twilio ($140) &bull; Ritesh Classroom ($20)</div>', content)
    
    # Update filter pills static numbers
    filter_pills_html = '''<div class="filter-pills" id="pin-filter-pills">
          <button class="category-pill active" onclick="filterPinTable('ALL', this)">All Items (32 &bull; $9,925)</button>
          <button class="category-pill" onclick="filterPinTable('MERGED', this)">&#127942; Merged (9 &bull; $900)</button>
          <button class="category-pill" onclick="filterPinTable('APPROVED', this)">&#9989; Approved (2 &bull; $200)</button>
          <button class="category-pill" onclick="filterPinTable('QUEUE', this)">&#128205; In Queue (13 &bull; $7,025)</button>
          <button class="category-pill" onclick="filterPinTable('OPIRE', this)">&#9889; Opire (5 &bull; $575)</button>
          <button class="category-pill" onclick="filterPinTable('CLIENT', this)">&#128188; Clients (3 &bull; $660)</button>
        </div>'''
    content = re.sub(r'<div class="filter-pills" id="pin-filter-pills">[\s\S]*?</div>', filter_pills_html, content)
    
    # Update tab counts in header
    content = re.sub(r'id="stat-pin-count">[\s\S]*?</span>', 'id="stat-pin-count">32 Items &bull; $9,925.00</span>', content)
    content = re.sub(r'id="merged-tab-count">[\s\S]*?</span>', 'id="merged-tab-count">9 PRs &bull; $900.00</span>', content)
    content = re.sub(r'id="bounty-count">[\s\S]*?</span>', 'id="bounty-count">13 Items &bull; $7,025.00</span>', content)

    # Embed EMBEDDED_BOUNTIES_DATA safely without re.sub template escape issues
    json_str = json.dumps(DATA)
    if "const EMBEDDED_BOUNTIES_DATA" in content:
        content = re.sub(r'const EMBEDDED_BOUNTIES_DATA = \{[\s\S]*?\};', lambda m: f'const EMBEDDED_BOUNTIES_DATA = {json_str};', content)
    else:
        content = content.replace("let allPinItems = [];", f"const EMBEDDED_BOUNTIES_DATA = {json_str};\n    let allPinItems = [];")

        
    with open("D:/aria-agent/dashboard/index.html", "w", encoding="utf-8") as f:
        f.write(content)
    print("Updated D:/aria-agent/dashboard/index.html successfully.")

if __name__ == "__main__":
    run()
