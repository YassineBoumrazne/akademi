from confluent_kafka import Producer
import json
import time

# Kafka bootstrap servers
bootstrap_servers = '192.168.0.100:9092'

# Kafka topic to produce messages to
kafka_topic = 'student_state'

# Kafka producer configuration
producer_config = {
    'bootstrap.servers': bootstrap_servers,
    # Add additional configuration parameters as needed
}


def delivery_report(err, msg):
    if err is not None:
        print('Message delivery failed: {}'.format(err))
    else:
        print('Message delivered to {} [{}]'.format(msg.topic(), msg.partition()))
def send_json_to_kafka(json_data):
    try:
        # Create Kafka producer instance
        producer = Producer(producer_config)

        # Produce JSON data as a string to Kafka topic
        producer.produce(kafka_topic, key=None, value=json.dumps(json_data), callback=delivery_report)

        # Wait for any outstanding messages to be delivered and delivery reports to be received
        producer.flush()

    except Exception as e:
        print(f'Error while sending message to Kafka: {e}')

if __name__ == '__main__':
    d = {
        "Dictionary": {
            "br1": {
                "class&": {
                    "Cdocopen": 0,
                    "Cdrow": 0,
                    "ClassEndTime": 0,
                    "ClassStartTime": 1708397586.7617724,
                    "Cpos": 0,
                    "Cyawn": 0
                },
                "yassin": {
                    "avgdocopen": 0.0,
                    "avgdrow": 0.0,
                }
            }
        }
    }
    iteration_counter = 1
    try:
        while True:
            send_json_to_kafka(d)
            # Increment the iteration counter
            iteration_counter += 1
            time.sleep(0.2)
    except KeyboardInterrupt:
        print("Received KeyboardInterrupt. Exiting the loop.")
