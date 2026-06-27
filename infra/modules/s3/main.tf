resource "aws_s3_bucket" "original" {
  bucket        = "${var.environment}-images-original-${var.account_id}"
  force_destroy = true
}

resource "aws_s3_bucket" "processed" {
  bucket        = "${var.environment}-images-processed-${var.account_id}"
  force_destroy = true
}

resource "aws_s3_bucket_cors_configuration" "original" {
  bucket = aws_s3_bucket.original.id

  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["GET", "PUT", "POST"]
    allowed_origins = ["*"]
    max_age_seconds = 3000
  }
}

resource "aws_s3_notification" "trigger_lambda" {
  bucket = aws_s3_bucket.original.id

  lambda_function {
    lambda_function_arn = var.lambda_arn
    events              = ["s3:ObjectCreated:*"]
  }
}
