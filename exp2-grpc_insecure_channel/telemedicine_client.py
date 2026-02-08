import grpc
import telemedicine_pb2
import telemedicine_pb2_grpc
import time


def unary_rpc(stub):
    print("\n[Unary RPC] Prescription")
    response = stub.GetPrescription(
        telemedicine_pb2.PatientRequest(
            patient_id="P101",
            symptoms="Fever and headache"
        )
    )
    print("Medicines:", response.medicines)
    print("Advice:", response.advice)


def server_streaming_rpc(stub):
    print("\n[Server Streaming RPC] Doctor Instructions")
    for instruction in stub.GetDoctorInstructions(
        telemedicine_pb2.PatientRequest(patient_id="P101")
    ):
        print("Instruction:", instruction.message)


def client_streaming_rpc(stub):
    print("\n[Client Streaming RPC] Sending Patient Vitals")

    def vitals():
        data = [
            ("Temperature", 98.4),
            ("Heart Rate", 76),
            ("Blood Pressure", 118)
        ]
        for t, v in data:
            print(f"Sending {t}: {v}")
            yield telemedicine_pb2.Vital(type=t, value=v)
            time.sleep(1)

    response = stub.SendVitals(vitals())
    print("Server Summary:", response.summary)


def bidirectional_streaming_rpc(stub):
    print("\n[Bidirectional Streaming RPC] Live Consultation")

    def messages():
        msgs = [
            "I am feeling dizzy",
            "Headache is severe",
            "Feeling better now"
        ]
        for msg in msgs:
            print("Patient:", msg)
            yield telemedicine_pb2.ChatMessage(
                sender="Patient",
                message=msg
            )
            time.sleep(1)

    for reply in stub.LiveConsultation(messages()):
        print("Doctor:", reply.message)


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
