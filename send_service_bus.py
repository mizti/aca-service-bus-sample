import asyncio
import os
from azure.servicebus.aio import ServiceBusClient
from azure.servicebus import ServiceBusMessage
from azure.identity.aio import DefaultAzureCredential
import json
from datetime import datetime

NAMESPACE_CONNECTION_STR = os.environ["SERVICE_BUS_CONNECTION_STR"]
QUEUE_NAME = os.environ["SERVICE_BUS_QUEUE_NAME"]

credential = DefaultAzureCredential()

s = '''{
    "timestamp": "%s",
    "message":"hello, service bus!",
    "key1": "value1",
    "key2": "value2",
    "key3": "value3",
    "nestedKey": {
        "nestedKey1": "nestedValue1"
    },
    "arrayKey": [
        "arrayValue1",
        "arrayValue2"
    ]
}''' % (datetime.now().isoformat()+"Z")

json_object =json.loads(s)
json_string = json.dumps(json_object, indent=2)

async def send_single_message(sender):
    # Create a Service Bus message and send it to the queue
    message = ServiceBusMessage(json_string)
    print(message)
    await sender.send_messages(message)
    print("Sent a single message")

async def send_a_list_of_messages(sender):
    # Create a list of messages and send it to the queue
    messages = [ServiceBusMessage(json_string) for i in range(5)]
    print(messages)
    await sender.send_messages(messages)
    print("Sent a list of 5 messages")

async def send_batch_message(sender):
    # Create a batch of messages
    async with sender:
        batch_message = await sender.create_message_batch()
        for i in range(10):
            try:
                # Add a message to the batch
                batch_message.add_message(ServiceBusMessage(json_string))
            except ValueError:
                # ServiceBusMessageBatch object reaches max_size.
                # New ServiceBusMessageBatch object can be created here to send more data.
                break
        # Send the batch of messages to the queue
        await sender.send_messages(batch_message)
    print("Sent a batch of 10 messages")

async def run():
    # create a Service Bus client using the connection string
    async with ServiceBusClient.from_connection_string(
        conn_str=NAMESPACE_CONNECTION_STR,
        logging_enable=True) as servicebus_client:
        # Get a Queue Sender object to send messages to the queue
        sender = servicebus_client.get_queue_sender(queue_name=QUEUE_NAME)
        async with sender:
            # Send one message
            await send_single_message(sender)
            # Send a list of messages
            #await send_a_list_of_messages(sender)
            # Send a batch of messages
            #await send_batch_message(sender)

asyncio.run(run())
print("Done sending messages")
print("-----------------------")
