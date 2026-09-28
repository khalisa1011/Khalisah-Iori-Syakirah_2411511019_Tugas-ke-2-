import multiprocessing as mp
import platform
import random
import time

MP_CONTEXT = 'spawn' if platform.system() == 'Windows' else 'fork'

JUMLAH_PROSES = 4
JUMLAH_ANGKA_PER_PROSES = 1_000_000


# ================= (a) MESSAGE PASSING dengan Queue =================
def jumlahkan_kirim_queue(proses_id, n_angka, hasil_queue, seed):
    random.seed(seed)
    subtotal = sum(random.randint(1, 100) for _ in range(n_angka))
    hasil_queue.put(subtotal)


def jalankan_versi_queue():
    ctx = mp.get_context(MP_CONTEXT)
    q = ctx.Queue()
    proses = [ctx.Process(target=jumlahkan_kirim_queue, args=(i, JUMLAH_ANGKA_PER_PROSES, q, i))
              for i in range(JUMLAH_PROSES)]
    start = time.perf_counter()
    for p in proses:
        p.start()
    subtotal_list = [q.get() for _ in range(JUMLAH_PROSES)]
    for p in proses:
        p.join()
    total = sum(subtotal_list)
    return total, time.perf_counter() - start


# ================= (b) SHARED MEMORY dengan Value + Lock =================
def jumlahkan_ke_shared(proses_id, n_angka, shared_total, lock, seed):
    random.seed(seed)
    subtotal = sum(random.randint(1, 100) for _ in range(n_angka))
    with lock:
        shared_total.value += subtotal


def jalankan_versi_value():
    ctx = mp.get_context(MP_CONTEXT)
    shared_total = ctx.Value('q', 0)  # 'q' = long long, cukup untuk total besar
    lock = ctx.Lock()
    proses = [ctx.Process(target=jumlahkan_ke_shared, args=(i, JUMLAH_ANGKA_PER_PROSES, shared_total, lock, i))
              for i in range(JUMLAH_PROSES)]
    start = time.perf_counter()
    for p in proses:
        p.start()
    for p in proses:
        p.join()
    return shared_total.value, time.perf_counter() - start


if __name__ == "__main__":
    print(f"Menggunakan mp context: '{MP_CONTEXT}'\n")

    total_q, waktu_q = jalankan_versi_queue()
    print(f"[Queue]  total = {total_q:,}   waktu = {waktu_q:.3f} detik")

    total_v, waktu_v = jalankan_versi_value()
    print(f"[Value]  total = {total_v:,}   waktu = {waktu_v:.3f} detik")

    print(f"\nSelisih waktu: {abs(waktu_q - waktu_v):.3f} detik")