# ReplicaValidationResult
PROCESS = 0
DISCARD = 1
STASH_VIEW = 2
STASH_WATERMARKS = 3
STASH_CATCH_UP = 4
STASH_WIATING_NEW_VIEW = 5

# ReplicaValidationReasons
INCORRECT_INSTANCE = "Incorrect instance"
INCORRECT_PP_SEQ_NO = "pp_seq_no must start from 1"
OUTSIDE_WATERMARKS = "Outside watermwarks"
FUTURE_VIEW = "Future view"
OLD_VIEW = "Old view"
CATCHING_UP = "Catching-up"
WAITING_FOR_NEW_VIEW = "Waiting for new view message"
GREATER_PREP_CERT = "Greater than last prepared certificate"
ALREADY_ORDERED = "Already ordered"
ALREADY_STABLE = "Already stable checkpoint"

