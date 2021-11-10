###################################################
#
#  NOTE: These variables will be dynamically 
#  loaded from the config.default file
#
###################################################

variable "GCP_PROJECT_ID" { 
    default = ""
}

variable "GCP_REGION" { 
    default = ""
}

variable "GCS_BUCKET_TEXT_DROPZONE" { 
    default = ""
}

variable "GCS_BUCKET_AUDIO_DROPZONE_SHORT" { 
    default = ""
}

variable "GCS_BUCKET_AUDIO_DROPZONE_LONG" { 
    default = ""
}

variable "GCS_BUCKET_CLOUD_FUNCTIONS" { 
    default = ""
}

variable "GCS_BUCKET_DATAFLOW" { 
    default = ""
}

variable "PUBSUB_TOPIC_TEXT_INPUT" { 
    default = ""
}

variable "PUBSUB_TOPIC_TEXT_SCORED" { 
    default = ""
}

variable "PUBSUB_TOPIC_TEXT_SCORED_PUSH_ENDPOINT" { 
    default = ""
}

variable "PUBSUB_TOPIC_TOXIC" { 
    default = ""
}

variable "BIGQUERY_DATASET" { 
    default = ""
}

variable "BIGQUERY_TABLE" { 
    default = ""
}

variable "BIGQUERY_LOCATION" { 
    default = ""
}
