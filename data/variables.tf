variable "region" {
  description = "AWS region"
  type        = string
  default     = "us-west-1"
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.micro"
}

variable "ami_id" {
  description = "AMI ID for the instance"
  type        = string
  default     = "ami-0c55b159cbfafe1f0" # Example AMI ID, replace with a valid one
}

variable "vpc_id" {
  description = "VPC ID where the instance will be launched"
  type        = string
}
