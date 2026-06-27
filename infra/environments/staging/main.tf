data "aws_caller_identity" "current" {}

module "dynamodb" {
  source      = "../../modules/dynamodb"
  environment = var.environment
}

module "lambda" {
  source               = "../../modules/lambda"
  environment          = var.environment
  original_bucket_arn  = module.s3.original_arn
  processed_bucket_arn = module.s3.processed_arn
  processed_bucket     = module.s3.processed_bucket
  dynamodb_table_arn   = module.dynamodb.table_arn
  dynamodb_table       = module.dynamodb.table_name
  lambda_zip           = "${path.module}/../../../lambda/lambda.zip"
  pillow_layer_arn     = "arn:aws:lambda:us-east-1:770693421928:layer:Klayers-p312-Pillow:9"
}

module "s3" {
  source      = "../../modules/s3"
  environment = var.environment
  account_id  = data.aws_caller_identity.current.account_id
  lambda_arn  = module.lambda.lambda_arn
}
