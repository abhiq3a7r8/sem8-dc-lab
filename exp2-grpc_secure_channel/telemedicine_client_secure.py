import grpc
import telemedicine_pb2
import telemedicine_pb2_grpc
import time
from datetime import datetime


def unary_rpc(stub):
    print("\n[SECURE UNARY RPC] Requesting prescription")

    start = time.perf_counter()
    response = stub.GetPrescription(
        telemedicine_pb2.PatientRequest(
            patient_id="P101",
            symptoms="Fever, headache"
        )
    )
    end = time.perf_counter()

    print("Medicines:", response.medicines)
    print("Advice:", response.advice)
    print(f"Latency: {(end - start) * 1000:.2f} ms")


def server_streaming_rpc(stub):
    print("\n[SECURE SERVER STREAMING RPC] Doctor instructions\n")

    prev_time = time.perf_counter()
    count = 0

    for instruction in stub.GetDoctorInstructions(
        telemedicine_pb2.PatientRequest(patient_id="P101")
    ):
        now = time.perf_counter()
        latency = now - prev_time

        print(
            f"[{datetime.now()}] {instruction.message} "
            f"(Latency: {latency:.2f} sec)"
        )

        prev_time = now
        count += 1

    print(f"\nTotal instructions received: {count}")


def client_streaming_rpc(stub):
    print("\n[SECURE CLIENT STREAMING RPC] Sending vitals\n")

    vitals_data = [
        ("HeartRate_bpm", 78),
        ("SpO2_percent", 97),
        ("SystolicBP_mmHg", 120),
        ("DiastolicBP_mmHg", 80),
        ("BodyTemperature_C", 37.0)
    ]

    def vitals_generator():
        for v_type, value in vitals_data:
            print(f"[{datetime.now()}] Sending {v_type}: {value}")
            yield telemedicine_pb2.Vital(type=v_type, value=value)
            time.sleep(1)

    start = time.perf_counter()
    response = stub.SendVitals(vitals_generator())
    end = time.perf_counter()

    print("\nServer Summary:", response.summary)
    print(f"Total streaming latency: {(end - start):.2f} sec")


def bidirectional_streaming_rpc(stub):
    print("\n[SECURE BIDIRECTIONAL STREAMING RPC] Live consultation\n")

    messages = [
        "Mild chest discomfort",
        "Breathing normal",
        "No dizziness"
    ]

    send_times = {}

    def chat_generator():
        for msg in messages:
            send_times[msg] = time.perf_counter()
            print(f"[{datetime.now()}] Patient:", msg)
            yield telemedicine_pb2.ChatMessage(
                sender="Patient",
                message=msg
            )
            time.sleep(1)

    replies = 0

    for response in stub.LiveConsultation(chat_generator()):
        recv_time = time.perf_counter()
        sent_msg = messages[replies]
        rtt = (recv_time - send_times[sent_msg]) * 1000

        print(
            f"[{datetime.now()}] Doctor: {response.message} "
            f"(RTT: {rtt:.2f} ms)"
        )
        replies += 1

    print(f"\nDoctor replies received: {replies}")


def main():
    with open("certs/ca.crt", "rb") as f:
        trusted_certs = f.read()

    credentials = grpc.ssl_channel_credentials(
        root_certificates=trusted_certs
    )

    with grpc.secure_channel("localhost:50053", credentials) as channel:
        stub = telemedicine_pb2_grpc.TelemedicineServiceStub(channel)

        while True:
            print("\n====== SECURE TELEMEDICINE gRPC MENU ======")
            print("1. Unary RPC – Prescription")
            print("2. Server Streaming – Doctor Instructions")
            print("3. Client Streaming – Send Vitals")
            print("4. Bidirectional Streaming – Live Consultation")
            print("5. Exit")

            choice = input("Enter choice: ")

            if choice == "1":
                unary_rpc(stub)
            elif choice == "2":
                server_streaming_rpc(stub)
            elif choice == "3":
                client_streaming_rpc(stub)
            elif choice == "4":
                bidirectional_streaming_rpc(stub)
            elif choice == "5":
                break
            else:
                print("Invalid choice")


if __name__ == "__main__":
    main()
