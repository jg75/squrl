#! /bin/bash

ship-it() {
    local bucket=$1
    local distribution=$2

    echo aws s3 sync www s3://$bucket/www --delete

    echo aws cloudfront \
        create-invalidation \
        --distribution-id $distribution \
        --paths '/www/*'

    echo sam deploy something or other
}

case $CODEBUILD_INITIATOR in
    codepipeline/squrl) ship-it www.squrl.com blahblah
        ;;
esac
