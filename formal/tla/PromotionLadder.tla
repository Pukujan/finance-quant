----------------------------- MODULE PromotionLadder -----------------------------
EXTENDS Naturals

CONSTANTS Candidates
States == {"IDLE", "SEALED", "RUNNING", "SCORED", "REVIEW", "PAPER", "TINY_LIVE", "REJECTED"}
variables state, current, authorityRecords

Init == /\ state = "IDLE" /\ current = "" /\ authorityRecords = [c \in Candidates |-> 0]
Seal(c) == /\ state = "IDLE" /\ c \in Candidates /\ state' = "SEALED" /\ current' = c /\ UNCHANGED authorityRecords
Run == /\ state = "SEALED" /\ state' = "RUNNING" /\ UNCHANGED <<current, authorityRecords>>
Score == /\ state = "RUNNING" /\ state' = "SCORED" /\ UNCHANGED <<current, authorityRecords>>
Review == /\ state = "SCORED" /\ state' = "REVIEW" /\ UNCHANGED <<current, authorityRecords>>
PaperApprove == /\ state = "REVIEW" /\ state' = "PAPER" /\ authorityRecords' = [authorityRecords EXCEPT ![current] = @ + 1] /\ UNCHANGED current
Reject == /\ state \in {"REVIEW", "SCORED"} /\ state' = "REJECTED" /\ UNCHANGED <<current, authorityRecords>>
TinyLiveApprove == /\ state = "PAPER" /\ state' = "TINY_LIVE" /\ UNCHANGED <<current, authorityRecords>>
Next == \E c \in Candidates: Seal(c) \/ Run \/ Score \/ Review \/ PaperApprove \/ Reject \/ TinyLiveApprove
TypeOK == /\ state \in States /\ current \in {""} \cup Candidates /\ authorityRecords \in [Candidates -> Nat]
NoAuthorityBeforeReview == state \in {"IDLE", "SEALED", "RUNNING", "SCORED", "REVIEW"} => \A c \in Candidates: authorityRecords[c] = 0
NoDuplicateAuthority == \A c \in Candidates: authorityRecords[c] <= 1
=============================================================================
