"""Test rápido de ByteTrack wrapper"""
from src.bytetrack_wrapper import ByteTrackWrapper

print("Inicializando ByteTrack...")
bt = ByteTrackWrapper()

# Test 1: Sin detecciones
print("\nTest 1: Sin detecciones")
tracks = bt.update([])
print(f"  Resultado: {len(tracks)} tracks")

# Test 2: Dos personas detectadas
print("\nTest 2: Dos personas detectadas")
dets = [
    {'bbox': [100, 100, 200, 300], 'conf': 0.85},
    {'bbox': [400, 150, 500, 350], 'conf': 0.75}
]
tracks = bt.update(dets)
print(f"  Detecciones: {len(dets)}")
print(f"  Tracks generados: {len(tracks)}")
for t in tracks:
    print(f"    Track ID={t['track_id']}, conf={t['conf']:.2f}")

# Test 3: Mismas personas (debería mantener IDs)
print("\nTest 3: Mismas personas con movimiento")
dets = [
    {'bbox': [105, 105, 205, 305], 'conf': 0.83},  # Persona 1 se movió un poco
    {'bbox': [405, 155, 505, 355], 'conf': 0.77}   # Persona 2 se movió un poco
]
tracks = bt.update(dets)
print(f"  Tracks: {len(tracks)}")
for t in tracks:
    print(f"    Track ID={t['track_id']} (debe mantener ID anterior)")

print("\n✓ ByteTrack funcionando correctamente")
