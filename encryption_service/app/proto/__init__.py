"""
Proto package.

Este paquete contiene la definición del contrato gRPC (.proto)
y los archivos generados (_pb2.py, _pb2_grpc.py).

Para regenerar los archivos, ejecuta desde el directorio encryption_service:
    & ".venv\\Scripts\\python.exe" -m grpc_tools.protoc ^
        -I./app/proto ^
        --python_out=./app/proto ^
        --grpc_python_out=./app/proto ^
        ./app/proto/encryption.proto
"""
