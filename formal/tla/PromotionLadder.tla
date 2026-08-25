----------------------------- MODULE PromotionLadder -----------------------------
EXTENDS Naturals

\* A deliberately small TLC model of FQ-PROP-005. Retry is observable, but it
\* cannot advance the ladder or create an authority record. Authority records are
\* durable historical receipts; pre-review constraints apply to the active candidate.
\* Candidate identity is immutable: an already-approved identity cannot be resealed.
CONSTANTS Candidates, MaxRetries
States == {"IDLE", "SEALED", "CAMPAIGN_RUNNING", "SCORED", "REVIEW",
           "PAPER_APPROVED", "TINY_LIVE_APPROVED", "REJECTED"}
VARIABLES state, current, authorityRecords, retries, reviewed

Init == /\ state = "IDLE"
        /\ current = ""
        /\ authorityRecords = [c \in Candidates |-> 0]
        /\ retries = 0
        /\ reviewed = FALSE

Seal(c) == /\ state = "IDLE"
           /\ c \in Candidates
           /\ authorityRecords[c] = 0
           /\ state' = "SEALED"
           /\ current' = c
           /\ retries' = 0
           /\ reviewed' = FALSE
           /\ UNCHANGED authorityRecords

Run == /\ state = "SEALED"
       /\ state' = "CAMPAIGN_RUNNING"
       /\ UNCHANGED <<current, authorityRecords, retries, reviewed>>

Retry == /\ state = "CAMPAIGN_RUNNING"
         /\ retries < MaxRetries
         /\ retries' = retries + 1
         /\ UNCHANGED <<state, current, authorityRecords, reviewed>>

Score == /\ state = "CAMPAIGN_RUNNING"
         /\ state' = "SCORED"
         /\ UNCHANGED <<current, authorityRecords, retries, reviewed>>

Review == /\ state = "SCORED"
          /\ state' = "REVIEW"
          /\ reviewed' = TRUE
          /\ UNCHANGED <<current, authorityRecords, retries>>

PaperApprove == /\ state = "REVIEW"
                /\ reviewed
                /\ authorityRecords[current] = 0
                /\ state' = "PAPER_APPROVED"
                /\ authorityRecords' = [authorityRecords EXCEPT ![current] = @ + 1]
                /\ UNCHANGED <<current, retries, reviewed>>

Reject == /\ state \in {"SCORED", "REVIEW"}
          /\ state' = "REJECTED"
          /\ UNCHANGED <<current, authorityRecords, retries, reviewed>>

TinyLiveApprove == /\ state = "PAPER_APPROVED"
                   /\ state' = "TINY_LIVE_APPROVED"
                   /\ UNCHANGED <<current, authorityRecords, retries, reviewed>>

Reset == /\ state \in {"PAPER_APPROVED", "TINY_LIVE_APPROVED", "REJECTED"}
         /\ state' = "IDLE"
         /\ current' = ""
         /\ retries' = 0
         /\ reviewed' = FALSE
         /\ UNCHANGED authorityRecords

Next == \E c \in Candidates:
          Seal(c) \/ Run \/ Retry \/ Score \/ Review \/ PaperApprove \/ Reject
          \/ TinyLiveApprove \/ Reset

TypeOK == /\ state \in States
          /\ current \in {""} \cup Candidates
          /\ authorityRecords \in [Candidates -> Nat]
          /\ retries \in 0..MaxRetries
          /\ reviewed \in BOOLEAN

NoAuthorityBeforeReview ==
    state \in {"SEALED", "CAMPAIGN_RUNNING", "SCORED", "REVIEW"}
    => authorityRecords[current] = 0
NoDuplicateAuthority == \A c \in Candidates: authorityRecords[c] <= 1
ApprovalRequiresReview == state = "PAPER_APPROVED" => reviewed
=============================================================================
