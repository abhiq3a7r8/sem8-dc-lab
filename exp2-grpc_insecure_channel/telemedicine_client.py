import grpc
import telemedicine_pb2
import telemedicine_pb2_grpc
import time


def unary_rpc(stub):
    print("\n[Unary RPC] Prescription")

    start = time.perf_counter()
    response = stub.GetPrescription(
        telemedicine_pb2.PatientRequest(
            patient_id="P101",
            symptoms="Fever and headache"
        )
    )
    end = time.perf_counter()

    print("Medicines:", response.medicines)
    print("Advice:", response.advice)
    print(f"Unary latency: {(end - start) * 1000:.2f} ms")


def server_streaming_rpc(stub):
    print("\n[Server Streaming RPC] Doctor Instructions")

    request_time = time.perf_counter()
    count = 0

    for instruction in stub.GetDoctorInstructions(
        telemedicine_pb2.PatientRequest(patient_id="P101")
    ):
        recv_time = time.perf_counter()
        latency = recv_time - request_time

        print(
            f"Instruction {count + 1}: {instruction.message} "
            f"(Latency: {latency:.2f} sec)"
        )

        request_time = recv_time
        count += 1

    print(f"Total instructions received: {count}")


def client_streaming_rpc(stub):
    print("\n[Client Streaming RPC] Sending Patient Vitals")

    vitals_data = [
        ("BodyTemperature_C", 37.0),
        ("HeartRate_bpm", 76),
        ("SpO2_percent", 97),
        ("SystolicBP_mmHg", 118),
        ("DiastolicBP_mmHg", 78)
    ]

    send_times = {}

    def vitals():
        for v_type, value in vitals_data:
            send_times[v_type] = time.perf_counter()
            print(f"Sending {v_type}: {value}")
            yield telemedicine_pb2.Vital(
                type=v_type,
                value=value
            )
            time.sleep(1)

    start = time.perf_counter()
    response = stub.SendVitals(vitals())
    end = time.perf_counter()

    print("Server Summary:", response.summary)
    print(f"Total client streaming latency: {(end - start):.2f} sec")


def bidirectional_streaming_rpc(stub):
    print("\n[Bidirectional Streaming RPC] Live Consultation")

    messages_data = [
        "Dizziness observed",
        "Severe headache persists",
        "Vitals stabilized",
        "Symptoms improving"
    ]

    send_times = {}

    def messages():
        for msg in messages_data:
            send_times[msg] = time.perf_counter()
            print("Patient:", msg)
            yield telemedicine_pb2.ChatMessage(
                sender="Patient",
                message=msg
            )
            time.sleep(1)

    replies = 0

    for reply in stub.LiveConsultation(messages()):
        recv_time = time.perf_counter()

        # Match reply with last sent message (lab-safe assumption)
        last_sent_msg = messages_data[replies]
        latency = recv_time - send_times[last_sent_msg]

        print(
            f"Doctor: {reply.message} "
            f"(RTT Latency: {latency:.2f} sec)"
        )

        replies += 1

    print(f"Doctor replies received: {replies}")


def main():
    with grpc.insecure_channel("localhost:50052") as channel:
        stub = telemedicine_pb2_grpc.TelemedicineServiceStub(channel)

        while True:
            print("\n========== Telemedicine gRPC Menu ==========")
            print("1. Unary RPC – Get Prescription")
            print("2. Server Streaming RPC – Doctor Instructions")
            print("3. Client Streaming RPC – Send Vitals")
            print("4. Bidirectional Streaming RPC – Live Consultation")
            print("5. Exit")

            choice = input("Enter your choice: ")

            if choice == "1":
                unary_rpc(stub)
            elif choice == "2":
                server_streaming_rpc(stub)
            elif choice == "3":
                client_streaming_rpc(stub)
            elif choice == "4":
                bidirectional_streaming_rpc(stub)
            elif choice == "5":
                print("Exiting client...")
                break
            else:
                print("Invalid choice! Try again.")


if __name__ == "__main__":
    main()
