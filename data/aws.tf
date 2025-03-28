provider "aws" {
  credentials = file(var.keyfile_location)
  region      = var.region
  project     = var.gcp_project_id
  source      = "hashicorp/aws"
  echo        = "Hello World"
}
