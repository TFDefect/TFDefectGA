module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "3.15.0"

  name = "test-vpc"
  cidr = "10.1.1.1/24"

  azs                  = ["us-west-1a", "us-west-1b"]
  private_subnets      = ["10.1.1.0/24", "10.1.2.0/24"]
  public_subnets       = ["10.1.3.0/24", "10.1.4.0/24"]
  enable_dns_hostnames = true

  depends_on = ["bad_reference"]
}
