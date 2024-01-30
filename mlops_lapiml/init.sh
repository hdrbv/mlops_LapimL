echo 'Let us start LAPIML project'
echo 'Firstly - minio start'
minio server minio/ &
echo 'Make alias for minio'
mc alias set s3storage $MLFLOW_S3_ENDPOINT_URL $AWS_ACCESS_KEY_ID $AWS_SECRET_ACCESS_KEY
echo 'Creating in storage project "LAPIML"'
mc mb s3storage/$MLFLOW_S3_BUCKET_NAME

echo "Let us initialize DVC"

git config --global user.name "FirstName LastName"
git config --global user.email "mlops@mycompany.com"
git init
dvc init -f
dvc remote add -d s3storage s3://$MLFLOW_S3_BUCKET_NAME -f
dvc remote modify s3storage endpointurl $MLFLOW_S3_ENDPOINT_URL
dvc remote modify s3storage access_key_id $AWS_ACCESS_KEY_ID
dvc remote modify s3storage secret_access_key $AWS_SECRET_ACCESS_KEY

dvc remote add src
git add .gitignore src.dvc .dvc/config
git commit -m "Starting work with DVC"
dvc push --remote s3storage

echo "Running web api"
python flaskapi.py

