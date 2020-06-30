First uncompress models.tar.gz

tar -xf models.tar.gz

then build the predictor

docker build -t yourname/predictor .

then  push to the docker hub 

docker push yourname/predictor

if you want to pass port number as an argument for table service you can invoke with

docker run -it yourname/predictor 8050


