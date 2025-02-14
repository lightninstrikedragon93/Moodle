import grpc
import auth_pb2 as auth_pb2
import auth_pb2_grpc as auth_pb2_grpc

def run():
    # Conectare la serverul gRPC
    channel = grpc.insecure_channel('localhost:50051')
    stub = auth_pb2_grpc.AuthServiceStub(channel)

    # Testare funcție Authenticate
    print("Testare funcție Authenticate:")
    auth_request = auth_pb2.AuthRequest(username="student2", password="student2")
    auth_response = stub.Authenticate(auth_request)
    print(f"Răspuns de la Authenticate: {auth_response}")

    print(f"Token type: {type(auth_response.token)}")  # Verifică tipul token-ului
    print(f"Token content: {auth_response.token}")  

    # Testare funcție ValidateToken
    print("\nTestare funcție ValidateToken:")
    validate_request = auth_pb2.TokenRequest(token=auth_response.token)
    
    print(f"validate request type: {type(validate_request)}")
    print(f"validate request content: {validate_request}")

    validate_response = stub.ValidateToken(validate_request)
    print(f"Răspuns de la ValidateToken: {validate_response}")

    # Testare funcție DestroyToken
    print("\nTestare funcție DestroyToken:")
    destroy_request = auth_pb2.TokenRequest(token=auth_response.token)
    destroy_response = stub.DestroyToken(destroy_request)
    print(f"Răspuns de la DestroyToken: {destroy_response}")

    # Testare ValidateToken după ce token-ul a fost distrus
    print("\nTestare ValidateToken după ce token-ul a fost distrus:")
    validate_response_after_destroy = stub.ValidateToken(validate_request)
    print(f"Răspuns de la ValidateToken după distrugere: {validate_response_after_destroy}")

if __name__ == '__main__':
    run()