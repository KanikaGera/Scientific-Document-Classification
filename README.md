Problem Statement
The objective of this project is to read the metadata of a scientific document available on arxiv.org and pass it to a predictor implemented as microservice on AWS, to classify it, and then store the results in sql database which is hosted on oracle cloud.

Solution Design



The figure above shows major components of the implemented solution. User first interacts with the web-
interface as explained below :

1. Web Interface
Interface offers search-engine where user can search according to author or title of the paper. User can
search either via complete name or via keywords. The page retrieves top 10 results matching the user query ,
sorted with respect to most recently updated paper .These results are then sent to SQS for prediction
purpose.
Idea is to show top 10 results to the user , which consist of Title , Author and Class of the paper.
The predictor task , 3 instances of the task running on each cluster machine, does the following work :

2. Predictor Task
ECS Predictor Task runs kgera96/cloudassignment:predictionservice_kg Docker container in Amazon ECS Specified Docker Container is Linux image, it runs a code that reads the data from amazon-queue, predictsand sends the data to table service using REST API. The prediction is done with the help of pre-trained models stored in the container.

Pre trained models are specifically Linear Discriminant Analysis, Random Forest and Boosted Decision Tree.

The table task is bound to specific port i.e. 8085 port, hence only one instance of this task runs on each cluster machine. It is programmed to bound to specific port so that predictor-service knows exact port to communicate. This is done , by keeping in mind future possibility that if we want another table-service task
that writes the prediction to some other database other than MySQL database , we can bind that table-service task to some other port , and hence predictor service would know exactly which port to refer to write to a particular database.

3. Table Writing Task
ECS Table Writing Task runs kgera96/cloudassignment:tableservice_new Docker container in Amazon ECS. Specified Docker Container is Linux image, it runs a code that reads the data provided by prediction service
and writes the data into MySQL database hosted on Oracle with the help of python-mySQL interface.
The results are fetched from MySQL database by webserver (hosted on local machine now) and shown to user on webpage.

Results
1. Machine Learning Model Training

	Dataset
		arxiv.org is a collection of millions of scientific 			documents. The metadata of various documents containing 		the title, abstract, and the category of various papers 		is used to train various Machine Learning Models .
	
	Data Pre-processing
		Abstract of paper is converted into BagOfWords and Tf-			IDF Matrix . Papers are classified into four major 			categories Physics, Maths, Biology, Computer Science 			and Finance.

	Models Trained
	1. K-Means
Tf-IDF matrix is used for training. Dataset is split into training and testing using KFolds with number of splits =2 and shuffle is True.
Test Accuracy = 53.13%

2. Linear Discriminant Analysis
BagOfWords matrix is used for training. Train and Test data split is 2:1.
Best Cross Validation Score is 0.643.
Test Accuracy is 65.77 %.

3. Random Forest
BagOfWords matrix is used for training. GridSearch is used to find the best combination of
hyper-parameters . Train and Test data split is 2:1
Best Parameters were n_estimators = 55 and max_depth=55.
Best Cross Validation Score = 0.777
Test Accuracy is 78.55%

4. Gradient Boosting Decision Tree
BagOfWords matrix is used for training. GridSearch is used to find the best combination of
hyper-parameters . Train and Test data split is 2:1
Best Parameters were n_estimators = 95 and max_depth=10.
Best Cross Validation Score = 0.763
Test Accuracy is 78.35%

2. Time to Predict
Step 1: Search, Retrieve Metadata, Parse Metadata, Upload to SQS
Average Time Taken = 5.54 sec/ 9 messages. 1 message = meta data of 1 article
Step 2: Retrieve Data from SQS, Predict, Send Prediction to Table Service
	Average Time Taken = 5.6 sec/ message
	Step 3: Write Data into MySQL Database on cloud
		Average Time Taken = 5.30 sec/ entry
		1 entry is for 1 message i.e. for 1 article.
In the basic ECS cluster structure there are
3 Ec2 instances each running 3 Predictor Containers and 1 Table Service Containers.
Therefore, theoretically Time Taken = 5.54 + 5.6 + 5.3*3= 27.04 sec to predict per search query i.e.
for 9 messages.

Discussion

1. Machine Learning Models
From the models trained Random Forest is giving best accuracy, followed by Gradient Boosting and then
the Linear Discriminant Analysis. K-Means gives the worst accuracy of all. The best accuracy achieved is 78.55%.

2. Scalability
Since predictor service reads the message from SQS queue one by one to predict, the predictor service used converts the abstract of paper read from message to BagOfWords and then predicts using pre-trained model loaded in the container. Since abstract is limited in length, the task is neither CPU intensive nor memory
intensive. Hence ECS cluster shall never face resource exhaustiveness. Though scalability of the solution
depends on SQS queue as number of articles to be classified are first loaded to SQS queue. If more users shall access the web-portal at same time, number of messages uploaded to SQS queue can increase up to large number. Hence if number of EC2 instances would be less then it will take long time to predict for a
particular message. Thus, cluster here auto scales according to number of messages waiting in the queue.
Scale-out policy was tested by increasing the number of messages in the SQS queue and then verifying
Autoscaling group launched an additional EC2 instance.

3. Fault Tolerance
Each machine in ECS cluster having one copy of table microservice and atleast three copies of predictor
microservice. Thus, more than one number of microservice available on more than one machine as well as
multiple times on single machine also makes the system fault tolerant.

Drawbacks and Future Work
1. Machine Learning Models

Currently maximum accuracy achieved is 78.55%, this could be improved further by more hyper-parameter tuning. Deep-Learning could also be applied and tested.

2. Web Interface
Time Delay parameters on Web Interface has to be tuned, to show results added to MySQL Database
using that particular query.
Web Interface and Web Server can be deployed to cloud for fault-tolerance, scalability and
availability.

Code 

Currently this github repository consists of table-service and predictor-service code , and procedure to convert it into docker containers.
