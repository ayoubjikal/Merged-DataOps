resource "aws_iam_user" "this" {
  name = var.user_name
}
resource "aws_iam_policy" "s3_access" {
  name        = "${var.user_name}-s3-policy"
  description = "S3 access for DataOps user"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:ListBucket",
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject"
        ]
        Resource = flatten([
          for bucket in var.bucket_names : [
            "arn:aws:s3:::${bucket}",
            "arn:aws:s3:::${bucket}/*"
          ]
        ])
      }
    ]
  })
}
resource "aws_iam_user_policy_attachment" "attach" {
  user       = aws_iam_user.this.name
  policy_arn = aws_iam_policy.s3_access.arn
}

resource "aws_iam_access_key" "this" {
  user = aws_iam_user.this.name
}
