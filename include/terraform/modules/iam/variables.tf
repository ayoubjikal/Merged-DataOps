variable "user_name" {
  description = "IAM user name"
  type        = string
}

variable "bucket_names" {
  description = "List of S3 buckets the user can access"
  type        = list(string)
}