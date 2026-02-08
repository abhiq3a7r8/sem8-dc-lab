import grpc
import telemedicine_pb2
import telemedicine_pb2_grpc
import time
from datetime import datetime


def unary_rpc(stub):
    print("\n[SECURE UNARY] Requesting prescription...")
    response = stub.GetPrescription(
        telemedicine_pb2.PatientRequest(
            patient_id="P101",
            symptoms="Fever, headache"
        )
    )
    print(f"[RESPONSE] Medicines: {response.medicines}")
    print(f"[RESPONSE] Advice: {response.advice}")


def server_streaming_rpc(stub):
    print("\n[SECURE SERVER STREAMING] Receiving doctor logs...\n")
    for instruction in stub.GetDoctorInstructions(
        telemedicine_pb2.PatientRequest(patient_id="P101")
    ):
        print(f"[CLIENT LOG] {instruction.message}")


def client_streaming_rpc(stub):
    print("\n[SECURE CLIENT STREAMING] Sending live vitals...\n")

    def vitals_generator():
        vitals = [
            ("Heart Rate", "78 bpm"),
            ("SpO2", "97 %"),
            ("Blood Pressure", "120/80"),
            ("Temperature", "98.6 F")
        ]

        for v_type, value in vitals:
            log = f"{datetime.now()} | {v_type}: {value}"
            print(f"[CLIENT LOG] {log}")
            yield telemedicine_pb2.Vital(type=v_type, value=value)
            time.sleep(1)

    response = stub.SendVitals(vitals_generator())
    print("\n[SERVER RESPONSE]", response.summary)


def bidirectional_streaming_rpc(stub):
    print("\n[SECURE BIDIRECTIONAL STREAMING] Live consultation started\n")

    def chat_generator():
        messages = [
            "Doctor, I feel mild chest discomfort",
            "Breathing feels normal",
            "No dizziness currently"
        ]

        for msg in messages:
            log = f"{datetime.now()} | Patient: {msg}"
            print(f"[CLIENT LOG] {log}")
            yield telemedicine_pb2.ChatMessage(
                sender="Patient",
                message=msg
            )
            time.sleep(1)

    responses = stub.LiveConsultation(chat_generator())
    for response in responses:
        print(f"[SERVER LOG] {response.sender}: {response.message}")


def main():
    # 🔐 Load CA certificate
    with open("certs/ca.crt", "rb") as f:
        trusted_certs = f.read()

    credentials = grpc.ssl_channel_credentials(
        root_certificates=trusted_certs
    )

    with grpc.secure_channel("localhost:50053", credentials) as channel:
        stub = telemedicine_pb2_grpc.TelemedicineServiceStub(channel)

        while True:
            print("\n========== TELEMEDICINE gRPC MENU ==========")
            print("1. Unary RPC – Get Prescription")
            print("2. Server Streaming – Doctor Instructions")
            print("3. Client Streaming – Send Patient Vitals")
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
                print("Exiting secure telemedicine client.")
                break
            else:
                print("Invalid choice.")


if __name__ == "__main__":
    main()
