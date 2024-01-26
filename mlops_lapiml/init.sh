echo 'Let us start LAPIML project'
echo 'Firstly - minio start'
minio server minio/ &
echo 'Make alias for minio'
mc alias set s3storage $MLFLOW_S3_ENDPOINT_URL $AWS_ACCESS_KEY_ID $AWS_SECRET_ACCESS_KEY #http://127.0.0.1:9001 mlflow password
echo 'Creating in storage project "LAPIML"'
mc mb s3storage/MLFLOW_S3_BUCKET_NAME

echo "Let us initialize DVC"
dvc init -f --no-scm
dvc remote add s3storage s3://storage --local
dvc remote add -d s3storage s3://$MLFLOW_S3_BUCKET_NAME -f
dvc remote modify s3storage endpointurl $MLFLOW_S3_ENDPOINT_URL #http://127.0.0.1:9001
dvc remote modify s3storage access_key_id $AWS_ACCESS_KEY_ID
dvc remote modify s3storage secret_access_key $AWS_SECRET_ACCESS_KEY

echo "Running web api"
python flaskapi.py

