from concurrent import futures
import grpc
import time
from datetime import datetime

import telemedicine_pb2
import telemedicine_pb2_grpc


class TelemedicineService(telemedicine_pb2_grpc.TelemedicineServiceServicer):

    # Unary RPC (unchanged)
    def GetPrescription(self, request, context):
        print(f"[SERVER] Prescription request from Patient {request.patient_id}")
        return telemedicine_pb2.Prescription(
            medicines="Paracetamol, Vitamin C",
            advice="Rest and hydration"
        )

    # ✅ SERVER STREAMING with live logs
    def GetDoctorInstructions(self, request, context):
        instructions = [
            "Monitoring heart rate",
            "SpO2 level is stable",
            "No respiratory distress",
            "Continue current medication"
        ]

        for msg in instructions:
            log = f"{datetime.now()} | Doctor Log: {msg}"
            print(f"[SERVER STREAM] {log}")
            yield telemedicine_pb2.Instruction(message=log)
            time.sleep(1)

    # ✅ CLIENT STREAMING with vitals logging
    def SendVitals(self, request_iterator, context):
        print("[SERVER STREAM] Receiving patient vitals...")
        vitals_log = []

        for vital in request_iterator:
            log = f"{datetime.now()} | {vital.type}: {vital.value}"
            print(f"[SERVER STREAM] {log}")
            vitals_log.append(log)

        summary = "Vitals received successfully"
        print("[SERVER] All vitals received. Sending summary.")
        return telemedicine_pb2.VitalsSummary(summary=summary)

    # ✅ BIDIRECTIONAL STREAMING with live chat logs
    def LiveConsultation(self, request_iterator, context):
        for msg in request_iterator:
            print(f"[LIVE] Patient: {msg.message}")
            reply = f"{datetime.now()} | Acknowledged: {msg.message}"
            print(f"[LIVE] Doctor: {reply}")
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

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    telemedicine_pb2_grpc.add_TelemedicineServiceServicer_to_server(
        TelemedicineService(), server
    )

    server.add_secure_port("[::]:50053", server_credentials)
    server.start()
    print("🔐 Secure Telemedicine gRPC Server running on port 50053")
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
