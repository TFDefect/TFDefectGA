resource "aws_instance" "example" {
  # ami           = "ami-0c55b159cbfafe1f0d1"
  instance_type = "t2.micro"

  tags = {
    Name = "TestInstance"
  }
}
