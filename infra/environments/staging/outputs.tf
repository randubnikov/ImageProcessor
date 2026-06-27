output "original_bucket"  { value = module.s3.original_bucket }
output "processed_bucket" { value = module.s3.processed_bucket }
output "dynamodb_table"   { value = module.dynamodb.table_name }
output "lambda_name"      { value = module.lambda.lambda_function_name }
