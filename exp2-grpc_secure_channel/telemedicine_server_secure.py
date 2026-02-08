from concurrent import futures
import grpc
import time
import random
from datetime import datetime

import telemedicine_pb2
import telemedicine_pb2_grpc


class TelemedicineService(telemedicine_pb2_grpc.TelemedicineServiceServicer):

    # Unary RPC
    def GetPrescription(self, request, context):
        time.sleep(random.uniform(0.005, 0.040))

        print(f"[SERVER] Prescription request from {request.patient_id}")
        return telemedicine_pb2.Prescription(
            medicines="Paracetamol, Vitamin C",
            advice="Rest and hydration"
        )

    # Server Streaming RPC
    def GetDoctorInstructions(self, request, context):
        instructions = [
            "Heart rate within normal range",
            "SpO2 stable at 97%",
            "Blood pressure normal",
            "Continue medication"
        ]

        for msg in instructions:
            delay = random.uniform(0.6, 1.8)
            time.sleep(delay)

            log = f"{datetime.now()} | {msg}"
            print(f"[SERVER STREAM] {log} (delay={delay:.2f}s)")

            yield telemedicine_pb2.Instruction(message=log)

    # Client Streaming RPC
    def SendVitals(self, request_iterator, context):
        print("[SERVER] Receiving vitals")

        vitals = []
        for vital in request_iterator:
            delay = random.uniform(0.3, 1.2)
            time.sleep(delay)

            log = f"{datetime.now()} | {vital.type}:{vital.value}"
            print(f"[SERVER STREAM] {log} (delay={delay:.2f}s)")
            vitals.append(log)

        return telemedicine_pb2.VitalsSummary(
            summary="Vitals processed successfully"
        )

    # Bidirectional Streaming RPC
    def LiveConsultation(self, request_iterator, context):
        for chat in request_iterator:
            delay = random.uniform(0.2, 1.0)
            time.sleep(delay)

            reply = f"{datetime.now()} | Acknowledged: {chat.message}"
            print(f"[LIVE] Doctor reply after {delay:.2f}s")

            yield telemedicine_pb2.ChatMessage(
                sender="Doctor",
                message=reply
            )


def serve():
    with open("certs/server.key", "rb") as f:
        private_key = f.read()
    with open("certs/server.crt", "rb") as f:
        certificate_chain = f.read()

    server_credentials = grpc.ssl_server_credentials(
        [(private_key, certificate_chain)]
    )

    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10)
    )

    telemedicine_pb2_grpc.add_TelemedicineServiceServicer_to_server(
        TelemedicineService(), server
    )

    server.add_secure_port("[::]:50053", server_credentials)
    server.start()

    print("🔐 Secure Telemedicine gRPC Server running on port 50053")
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
