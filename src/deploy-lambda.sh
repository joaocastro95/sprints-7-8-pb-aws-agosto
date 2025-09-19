#!/bin/bash

URL_STRING=".dkr.ecr.us-east-1.amazonaws.com"

CONTAINER_STRING="adriano-bertanha/lambda-chatbot-telegram"

LAMBDA_FUNCTION="chatbot-telegram"

IMAGE_STRING="latest"

ECR_IMAGE_URI="$AWS_ACCOUNT_ID$URL_STRING/$CONTAINER_STRING:$IMAGE_STRING"

# log in to ECR
aws ecr get-login-password --region us-east-1 --profile adriano-bertanha | docker login --username AWS --password-stdin "$AWS_ACCOUNT_ID$URL_STRING"

# remove previous images to save space
docker rmi "$AWS_ACCOUNT_ID$URL_STRING/$CONTAINER_STRING"
docker rmi "$CONTAINER_STRING"

# build image
docker build --tag "$CONTAINER_STRING" .

# tag and push to AWS ECR
docker tag $CONTAINER_STRING:latest "$ECR_IMAGE_URI"
docker push "$ECR_IMAGE_URI"

# update Lambda
aws lambda update-function-code --function-name $LAMBDA_FUNCTION --image-uri "$ECR_IMAGE_URI" --profile adriano-bertanha

