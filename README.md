

## Usage

### Step 1: Start the Services

Open your terminal and run the following command to start the Docker services:

```bash
docker-compose up -d --build
```

### Step 2: Start the Flask Server

Open the first terminal and execute the following commands:

```bash
docker exec -it spark-hadoop-kafka-flask-app-1 /bin/bash
cd akademi
python server.py
```

### Step 3: Start the API Server

Open another terminal and run the following commands:

```bash
docker exec -it spark-hadoop-kafka-flask-app-1 /bin/bash
cd akademi/api_server
python serverf.py
```

### Step 4: Start the Kafka Consumer

Open another terminal and run the following commands:

```bash
docker exec -it da-spark-yarn-master /bin/bash
cd bigdata_project2/kafka_app
python consumer.py
```

Now, the application is running, and you can access it at [http://localhost:5500](http://localhost:5500). The data is stored on HDFS at the path `/user/student/`.

Keep the terminals running to ensure the continuous operation of the application. If you encounter any issues, refer to the application logs in the respective terminals for troubleshooting.

Enjoy using akademi