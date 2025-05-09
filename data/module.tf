module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "3.14.0"

  name = "test-vpc"
  cidr = "10.0.0.0/16"

  azs                  = ["us-west-1a", "us-west-1b"]
  private_subnets      = ["10.0.1.0/24", "10.0.2.0/24"]
  public_subnets       = ["10.0.3.0/24", "10.0.4.0/24"]
  enable_dns_hostnames = true

  depends_on = ["bad_reference"]
}
