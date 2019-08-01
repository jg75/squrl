#! /bin/bash
S3_DEPLOY_BUCKET=ae-sam-deploy

ship-it() {
    local api_version=$1
    local bucket=$2
    local distribution_id=$3

    sam build \
        --parameter-overrides \
            "ParameterKey=ApiVersionParameter,ParameterValue=$api_version
            ParameterKey=S3BucketParameter,ParameterValue=$bucket"

    sam package \
        --output-template-file sam-packaged.yml \
        --s3-bucket $S3_DEPLOY_BUCKET

    sam deploy \
        --capabilities CAPABILITY_IAM \
        --template-file sam-packaged.yml \
        --stack-name squrl-$api_version

    echo aws s3 sync www s3://$bucket/www --delete

    echo aws cloudfront \
        create-invalidation \
        --distribution-id $distribution_id \
        --paths '/www/*'
}

case $CODEBUILD_INITIATOR in
    codepipeline/squrl) ship-it v1 www.squrl.com distribution
        ;;
esac
