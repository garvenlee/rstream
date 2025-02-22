import asyncio
import time

from rstream import (
    AMQPMessage,
    DisconnectionErrorInfo,
    Producer,
)

STREAM = "my-test-stream"
MESSAGES = 10000000
connection_is_closed = False


async def publish():
    async def on_connection_closed(disconnection_info: DisconnectionErrorInfo) -> None:
        print(
            "connection has been closed from stream: "
            + str(disconnection_info.streams)
            + " for reason: "
            + str(disconnection_info.reason)
        )

        global connection_is_closed
        connection_is_closed = True

    print("creating Producer")
    # producer will be closed at the end by the async context manager
    # both if connection is still alive or not
    async with Producer(
        "localhost", username="guest", password="guest", connection_closed_handler=on_connection_closed
    ) as producer:

        # create a stream if it doesn't already exist
        await producer.create_stream(STREAM, exists_ok=True)

        # sending a million of messages in AMQP format
        start_time = time.perf_counter()

        print("Sending MESSAGES")
        for i in range(MESSAGES):
            amqp_message = AMQPMessage(
                body="hello: {}".format(i),
            )
            # send is asynchronous
            global connection_is_closed
            try:
                if connection_is_closed is False:
                    await producer.send(stream=STREAM, message=amqp_message)
                else:
                    break
            # manage exception
            except:
                print("Connection Closed")
                break

            if i % 10000 == 0:
                print("sent 10000 messages")

    end_time = time.perf_counter()
    print(f"Sent {MESSAGES} messages in {end_time - start_time:0.4f} seconds")


asyncio.run(publish())
