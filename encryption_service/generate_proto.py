"""
Script para generar los archivos _pb2.py y _pb2_grpc.py desde encryption.proto
y copiarlos al directorio de app_core.

Ejecutar desde el directorio encryption_service:
    & ".venv\\Scripts\\python.exe" generate_proto.py
"""
import subprocess
import sys
import os
import shutil

# Directorios clave
base_dir = os.path.dirname(os.path.abspath(__file__))
proto_dir = os.path.join(base_dir, "app", "proto")
proto_file = os.path.join(proto_dir, "encryption.proto")
app_core_proto_dir = os.path.join(base_dir, "..", "app_core", "app", "services", "proto")

print("=" * 60)
print("Helios — Creating Protobuf files")
print("=" * 60)
print(f"Proto dir:      {proto_dir}")
print(f"Proto file:     {proto_file}")
print(f"AppCore proto:  {app_core_proto_dir}")
print(f".proto existe:  {os.path.exists(proto_file)}")
print()

# --- Paso 1: Generar _pb2.py y _pb2_grpc.py ---
print("Generating stubs with grpc_tools.protoc...")
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

if result.returncode != 0:
    print(f"Error generating protobuf:")
    print(result.stderr)
    sys.exit(result.returncode)

print("Generated files in encryption_service/app/proto/:")
for f in sorted(os.listdir(proto_dir)):
    if f.endswith((".py", ".proto")):
        print(f"   - {f}")

# --- Paso 2: Parchar el archivo _grpc.py generado ---
# protoc genera imports absolutos (ej: import encryption_pb2)
# pero al estar dentro de un paquete Python se requieren imports relativos.
# También corregimos el nombre de la API de gRPC si está desactualizado.
print()
print("Patching generated encryption_pb2_grpc.py...")
grpc_file = os.path.join(proto_dir, "encryption_pb2_grpc.py")
with open(grpc_file, "r", encoding="utf-8") as fh:
    content = fh.read()

# Parche 1: import absoluto → relativo (obligatorio dentro de un paquete)
patched = content.replace(
    "import encryption_pb2 as encryption__pb2",
    "from . import encryption_pb2 as encryption__pb2  # patched: relative import",
)
# Parche 2: nombre de función incorrecto generado por versiones antiguas de protoc
patched = patched.replace(
    "grpc.method_handlers_generic_handler(",
    "grpc.method_service_handler(",
)

with open(grpc_file, "w", encoding="utf-8") as fh:
    fh.write(patched)

print("   Relative import patched in encryption_pb2_grpc.py")

# --- Paso 3: Copiar stubs a app_core ---
print()
print("Copying stubs to app_core/app/services/proto/...")
os.makedirs(app_core_proto_dir, exist_ok=True)

files_to_copy = ["encryption_pb2.py", "encryption_pb2_grpc.py"]
for filename in files_to_copy:
    src = os.path.join(proto_dir, filename)
    dst = os.path.join(app_core_proto_dir, filename)
    if os.path.exists(src):
        shutil.copy2(src, dst)
        print(f"   {filename} → app_core/app/services/proto/")
    else:
        print(f"    {filename} not found, skipping...")

print()
print("The service can now be started with:")
print('    & ".venv\\Scripts\\python.exe" run.py')
print("=" * 60)
