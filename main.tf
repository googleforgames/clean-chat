// Copyright 2021 Google LLC All Rights Reserved.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

// Run:
// terraform apply -var project="<YOUR_GCP_ProjectID>"

// TODO: 
//      Add unauthorized access for Cloud Functions

terraform {
  required_providers {
    google = {
      source = "google"
      version = "~> 3.84"
    }
    google-beta = {
      source = "google-beta"
      version = "~> 3.84"
    }
  }
}

/******************************************************

Enable Google Cloud Services

*******************************************************/

variable "gcp_service_list" {
  description ="The list of apis necessary for the project"
  type = list(string)
  default = [
    "storage.googleapis.com",
	"cloudfunctions.googleapis.com",
	"run.googleapis.com",
	"container.googleapis.com",
	"containerregistry.googleapis.com",
	"artifactregistry.googleapis.com",
	"cloudbuild.googleapis.com",
	"dataflow.googleapis.com",
	"speech.googleapis.com"
  ]
}

resource "google_project_service" "gcp_services" {
  for_each = toset(var.gcp_service_list)
  project = "${var.GCP_PROJECT_ID}"
  service = each.key
}

/******************************************************

Google Cloud Storage Resources

*******************************************************/

resource "google_storage_bucket" "text-dropzone" {
  name          = "${var.GCS_BUCKET_TEXT_DROPZONE}"
  location      = "US"
  storage_class = "STANDARD"
  force_destroy = true
  uniform_bucket_level_access = true
}

resource "google_storage_bucket" "audio-dropzone-short" {
  name          = "${var.GCS_BUCKET_AUDIO_DROPZONE_SHORT}"
  location      = "US"
  storage_class = "STANDARD"
  force_destroy = true
  uniform_bucket_level_access = true
}

resource "google_storage_bucket" "audio-dropzone-long" {
  name          = "${var.GCS_BUCKET_AUDIO_DROPZONE_LONG}"
  location      = "US"
  storage_class = "STANDARD"
  force_destroy = true
  uniform_bucket_level_access = true
}

resource "google_storage_bucket" "gcs-for-cloud-functions" {
  name          = "${var.GCS_BUCKET_CLOUD_FUNCTIONS}"
  location      = "US"
  storage_class = "STANDARD"
  force_destroy = true
  uniform_bucket_level_access = true
}


resource "google_storage_bucket" "dataflow-bucket" {
  name          = "${var.GCS_BUCKET_DATAFLOW}"
  location      = "US"
  storage_class = "STANDARD"
  force_destroy = true
  uniform_bucket_level_access = true
}

resource "google_storage_bucket_object" "dataflow-staging-setup" {
  name   = "staging/setup.txt"
  content = "Used for setup"
  bucket = google_storage_bucket.dataflow-bucket.name
}

resource "google_storage_bucket_object" "dataflow-tmp-setup" {
  name   = "tmp/setup.txt"
  content = "Used for setup"
  bucket = google_storage_bucket.dataflow-bucket.name
}

/******************************************************

Google PubSub Resources

*******************************************************/

resource "google_pubsub_topic" "text-input" {
  name = "${var.PUBSUB_TOPIC_TEXT_INPUT}"
}

resource "google_pubsub_topic" "text-scored" {
  name = "${var.PUBSUB_TOPIC_TEXT_SCORED}"
}

resource "google_pubsub_topic" "toxic-topic" {
  name = "${var.PUBSUB_TOPIC_TOXIC}"
}

resource "google_pubsub_subscription" "text-scored-sub" {
  name  = "${var.PUBSUB_TOPIC_TEXT_SCORED}-sub"
  topic = google_pubsub_topic.text-scored.name

  ack_deadline_seconds = 20

  push_config {
    push_endpoint = "${var.PUBSUB_TOPIC_TEXT_SCORED_PUSH_ENDPOINT}"

    attributes = {
      x-goog-version = "v1"
    }
  }
  retry_policy {
    minimum_backoff = "10s"
    maximum_backoff = "120s"
  }
}

resource "google_pubsub_subscription" "toxic-topic-sub" {
  name  = "${var.PUBSUB_TOPIC_TOXIC}-sub"
  topic = google_pubsub_topic.toxic-topic.name

  message_retention_duration = "1200s"
  retain_acked_messages      = true
  ack_deadline_seconds       = 10
  enable_message_ordering    = false

  expiration_policy {
    ttl = "300000s"
  }
  retry_policy {
    minimum_backoff = "10s"
    maximum_backoff = "120s"
  }
}

/******************************************************

Google Cloud BigQuery Resources

*******************************************************/

resource "google_bigquery_dataset" "bigquery_dataset" {
  dataset_id    = "${var.BIGQUERY_DATASET}"
  friendly_name = "${var.BIGQUERY_DATASET}"
  description   = "Antidote Dataset"
  location      = "${var.BIGQUERY_LOCATION}"
  project       = "${var.GCP_PROJECT_ID}"
}

resource "google_bigquery_table" "bigquery_table_scored" {
  dataset_id = google_bigquery_dataset.bigquery_dataset.dataset_id
  table_id   = "${var.BIGQUERY_TABLE}"
  schema = <<EOF
[
    {
        "name": "username",
        "type": "STRING",
        "mode": "NULLABLE",
        "description": "unique username or user id"
    },
    {
        "name": "timestamp",
        "type": "INT64",
        "mode": "NULLABLE",
        "description": "Unix timestamp"
    },
    {
        "name": "text",
        "type": "STRING",
        "mode": "NULLABLE",
        "description": "text comment string"
    },
    {
        "name": "score",
        "type": "FLOAT64",
        "mode": "NULLABLE",
        "description": "toxicity score"
    }
]
EOF
}

/******************************************************

Google Cloud Functions Resources

*******************************************************/

data "archive_file" "cf-speech-to-text-short-zip" {
 type        = "zip"
 source_dir  = "./components/cloud_functions/speech_to_text_short"
 output_path = "./components/cloud_functions/speech_to_text_short.zip"
}

data "archive_file" "cf-speech-to-text-long-zip" {
 type        = "zip"
 source_dir  = "./components/cloud_functions/speech_to_text_long"
 output_path = "./components/cloud_functions/speech_to_text_long.zip"
}

data "archive_file" "cf-send-to-pubsub-zip" {
 type        = "zip"
 source_dir  = "./components/cloud_functions/send_to_pubsub"
 output_path = "./components/cloud_functions/send_to_pubsub.zip"
}

# Upload zipped cloud functions to Google Cloud Storage
resource "google_storage_bucket_object" "cf-speech-to-text-short-zip" {
 name   = "speech_to_text_short.zip"
 bucket = "${google_storage_bucket.gcs-for-cloud-functions.name}"
 source = "./components/cloud_functions/speech_to_text_short.zip"
}

resource "google_storage_bucket_object" "cf-speech-to-text-long-zip" {
 name   = "speech_to_text_long.zip"
 bucket = "${google_storage_bucket.gcs-for-cloud-functions.name}"
 source = "./components/cloud_functions/speech_to_text_long.zip"
}

resource "google_storage_bucket_object" "cf-send-to-pubsub-zip" {
 name   = "send_to_pubsub.zip"
 bucket = "${google_storage_bucket.gcs-for-cloud-functions.name}"
 source = "./components/cloud_functions/send_to_pubsub.zip"
}

resource "google_cloudfunctions_function" "cf-speech-to-text-short" {
  name                  = "antidote-speech-to-text-short"
  description           = "Antidote Speech-to-Text Short"
  source_archive_bucket = "${google_storage_bucket_object.cf-speech-to-text-short-zip.bucket}"
  source_archive_object = "${google_storage_bucket_object.cf-speech-to-text-short-zip.name}"
  runtime               = "python39"
  available_memory_mb   = 512
  max_instances         = 3
  timeout               = 120
  region                = "${var.GCP_REGION}"
  entry_point           = "main"
  
  environment_variables = {
    gcs_results_bucket = google_storage_bucket.text-dropzone.name
  }

  event_trigger {
      event_type = "google.storage.object.finalize"
      resource   = google_storage_bucket.audio-dropzone-short.name
  }

}

resource "google_cloudfunctions_function" "cf-speech-to-text-long" {
  name                  = "antidote-speech-to-text-long"
  description           = "Antidote Speech-to-Text Long"
  source_archive_bucket = "${google_storage_bucket_object.cf-speech-to-text-long-zip.bucket}"
  source_archive_object = "${google_storage_bucket_object.cf-speech-to-text-long-zip.name}"
  runtime               = "python39"
  available_memory_mb   = 1024
  max_instances         = 3
  timeout               = 480
  region                = "${var.GCP_REGION}"
  entry_point           = "main"
  
  environment_variables = {
    gcs_results_bucket = google_storage_bucket.text-dropzone.name
  }

  event_trigger {
      event_type = "google.storage.object.finalize"
      resource   = google_storage_bucket.audio-dropzone-long.name
  }

}

resource "google_cloudfunctions_function" "cf-send-to-pubsub" {
  name                  = "antidote-send-to-pubsub"
  description           = "Antidote send text to PubSub"
  source_archive_bucket = "${google_storage_bucket_object.cf-send-to-pubsub-zip.bucket}"
  source_archive_object = "${google_storage_bucket_object.cf-send-to-pubsub-zip.name}"
  runtime               = "python39"
  available_memory_mb   = 256
  max_instances         = 3
  timeout               = 120
  region                = "${var.GCP_REGION}"
  entry_point           = "main"
  
  environment_variables = {
    gcp_project_id = "${var.GCP_PROJECT_ID}"
    pubsub_topic = google_pubsub_topic.text-input.name
  }

  event_trigger {
      event_type = "google.storage.object.finalize"
      resource   = google_storage_bucket.text-dropzone.name
  }

}
