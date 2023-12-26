echo 'Let us start LAPIML project'
echo 'Firstly - minio start'
minio server minio/ &
echo 'Make alias for minio'
mc alias set s3storage http://127.0.0.1:9001 YOURS3ACCESSKEY YOURSECERTKE
echo 'Creating in storage project "LAPIML"'
mc mb s3storage/mlops_lapiml

echo "Let us initialize DVC"
dvc init -f
dvc remote remove s3storage
dvc remote add -d s3storage s3://mlops_lapiml -f
dvc remote modify s3storage endpointurl http://127.0.0.1:9001
dvc remote modify s3storage access_key_id YOURS3ACCESSKEY
dvc remote modify s3storage secret_access_key YOURSECERTKE

echo "Running web api"
python flaskapi.py

