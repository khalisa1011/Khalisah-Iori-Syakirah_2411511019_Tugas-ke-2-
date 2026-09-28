import multiprocessing as mp
import platform
import time
import os
import matplotlib.pyplot as plt

# Deteksi otomatis: Windows cuma dukung 'spawn', Linux/Mac defaultnya 'fork'
MP_CONTEXT = 'spawn' if platform.system() == 'Windows' else 'fork'


def hitung_prima(n):
    # Menghitung semua bilangan prima hingga n (algoritma sederhana, sengaja tidak dioptimasi)
    primes = []
    for num in range(2, n):
        is_prime = True
        for i in range(2, int(num ** 0.5) + 1):
            if num % i == 0:
                is_prime = False
                break
        if is_prime:
            primes.append(num)
    return len(primes)


if __name__ == "__main__":
    print(f"Sistem operasi terdeteksi : {platform.system()}")
    print(f"Menggunakan mp context    : '{MP_CONTEXT}'")
    print(f"Jumlah CPU tersedia       : {os.cpu_count()}\n")

    # 8 "tugas" independen -- supaya pengujian sampai 8 worker tetap bermakna
    daftar_n = [80_000] * 8

    # --- Baseline: SEKUENSIAL ---
    start = time.perf_counter()
    hasil_sequential = [hitung_prima(n) for n in daftar_n]
    waktu_sequential = time.perf_counter() - start
    print(f"[Sequential] waktu: {waktu_sequential:.3f} detik")

    daftar_worker = [1, 2, 4, 8]
    waktu_per_worker = {}

    for w in daftar_worker:
        start = time.perf_counter()
        with mp.get_context(MP_CONTEXT).Pool(processes=w) as pool:
            hasil_paralel = pool.map(hitung_prima, daftar_n)
        waktu = time.perf_counter() - start
        waktu_per_worker[w] = waktu
        speedup = waktu_sequential / waktu
        print(f"worker={w} -> waktu={waktu:.3f}s  speedup aktual={speedup:.2f}x  (Amdahl ideal P=1.0: {w}x)")

    # --- Plot: speedup aktual vs Amdahl ideal ---
    speedup_aktual = [waktu_sequential / waktu_per_worker[w] for w in daftar_worker]
    speedup_amdahl = [w for w in daftar_worker]  # P=1.0 -> speedup ideal = N

    plt.figure(figsize=(7, 4.5))
    plt.plot(daftar_worker, speedup_amdahl, linestyle='--', marker='s', color="#888888", label="Amdahl ideal (P=1.0)")
    plt.plot(daftar_worker, speedup_aktual, marker='o', color="#4C72B0", linewidth=2, label="Speedup aktual")
    plt.xlabel("Jumlah worker")
    plt.ylabel("Speedup (x)")
    plt.title(f"Speedup Aktual vs Kurva Amdahl (cpu_count={os.cpu_count()}, context={MP_CONTEXT})")
    plt.xticks(daftar_worker)
    plt.legend()
    plt.grid(alpha=0.3)
    plt.show()