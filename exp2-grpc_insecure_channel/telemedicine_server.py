from concurrent import futures
import grpc
import time
import random

import telemedicine_pb2
import telemedicine_pb2_grpc


class TelemedicineService(telemedicine_pb2_grpc.TelemedicineServiceServicer):

    # Unary RPC
    def GetPrescription(self, request, context):
        # Random processing delay (5–40 ms)
        time.sleep(random.uniform(0.005, 0.040))

        return telemedicine_pb2.Prescription(
            medicines="Paracetamol, Vitamin C",
            advice="Drink fluids and take rest"
        )

    # Server Streaming RPC
    def GetDoctorInstructions(self, request, context):
        instructions = [
            "Monitor temperature twice a day",
            "Avoid cold drinks",
            "Complete full medication course"
        ]

        for msg in instructions:
            # Random delay per instruction (0.6–1.8 sec)
            time.sleep(random.uniform(0.6, 1.8))
            yield telemedicine_pb2.Instruction(message=msg)

    # Client Streaming RPC
    def SendVitals(self, request_iterator, context):
        vitals_received = []

        for vital in request_iterator:
            # Random processing delay per vital (0.3–1.2 sec)
            time.sleep(random.uniform(0.3, 1.2))
            vitals_received.append(f"{vital.type}:{vital.value}")

        return telemedicine_pb2.VitalsSummary(
            summary="Vitals received -> " + ", ".join(vitals_received)
        )

    # Bidirectional Streaming RPC
    def LiveConsultation(self, request_iterator, context):
        for chat in request_iterator:
            # Random doctor response delay (0.2–1.0 sec)
            time.sleep(random.uniform(0.2, 1.0))

            yield telemedicine_pb2.ChatMessage(
                sender="Doctor",
                message=f"Received: {chat.message}"
            )


def serve():
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10)
    )

    telemedicine_pb2_grpc.add_TelemedicineServiceServicer_to_server(
        TelemedicineService(), server
    )

    server.add_insecure_port("[::]:50052")
    server.start()

    print("Telemedicine gRPC Server running on port 50052...")
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
