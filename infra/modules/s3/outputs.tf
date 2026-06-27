output "original_bucket"  { value = aws_s3_bucket.original.id }
output "processed_bucket" { value = aws_s3_bucket.processed.id }
output "original_arn"     { value = aws_s3_bucket.original.arn }
output "processed_arn"    { value = aws_s3_bucket.processed.arn }
