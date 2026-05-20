"""Script para generar los archivos _pb2.py y _pb2_grpc.py desde encryption.proto"""
import subprocess
import sys
import os

# Directorio raíz del proyecto encryption_service
base_dir = os.path.dirname(os.path.abspath(__file__))
proto_dir = os.path.join(base_dir, "app", "proto")
proto_file = os.path.join(proto_dir, "encryption.proto")

print(f"Proto dir: {proto_dir}")
print(f"Proto file: {proto_file}")
print(f"File exists: {os.path.exists(proto_file)}")

result = subprocess.run(
    [
        sys.executable, "-m", "grpc_tools.protoc",
        f"-I{proto_dir}",
        f"--python_out={proto_dir}",
        f"--grpc_python_out={proto_dir}",
        proto_file,
    ],
    capture_output=True,
    text=True,
)

if result.returncode == 0:
    print("✅ Archivos protobuf generados exitosamente:")
    for f in os.listdir(proto_dir):
        if f.endswith((".py", ".proto")):
            print(f"   - {f}")
else:
    print(f"❌ Error generando protobuf:")
    print(result.stderr)

sys.exit(result.returncode)
