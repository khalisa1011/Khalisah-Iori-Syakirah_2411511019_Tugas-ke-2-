import multiprocessing as mp
import platform
import time

MP_CONTEXT = 'spawn' if platform.system() == 'Windows' else 'fork'


def hitung_prima_kecil(n):
    primes = []
    for num in range(2, n):
        is_p = True
        for i in range(2, int(num ** 0.5) + 1):
            if num % i == 0:
                is_p = False
                break
        if is_p:
            primes.append(num)
    return len(primes)


def producer(q, jumlah_item, nama="Producer"):
    for i in range(jumlah_item):
        item = 30_000 + i * 1000   # tiap item = "tugas" hitung n bilangan prima (CPU-bound)
        q.put(item)
        print(f"[{nama}] menghasilkan tugas: n={item}")
    q.put(None)


def consumer(q, nama="Consumer"):
    while True:
        item = q.get()
        if item is None:
            q.put(None)
            break
        hasil = hitung_prima_kecil(item)
        print(f"    [{nama}] memproses n={item} -> jumlah prima={hasil}")


if __name__ == "__main__":
    print(f"Menggunakan mp context: '{MP_CONTEXT}'\n")

    ctx = mp.get_context(MP_CONTEXT)
    q = ctx.Queue()

    start = time.perf_counter()
    p_producer = ctx.Process(target=producer, args=(q, 6))
    p_consumers = [ctx.Process(target=consumer, args=(q, f"Consumer-{i+1}")) for i in range(3)]

    p_producer.start()
    for p in p_consumers:
        p.start()

    p_producer.join()
    for p in p_consumers:
        p.join()
    waktu = time.perf_counter() - start

    print(f"\nSemua tugas selesai diproses oleh 3 consumer (proses terpisah).")
    print(f"Waktu total: {waktu:.3f} detik")