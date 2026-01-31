import pandas as pd
import numpy as np
import random

# --- KONFIGURASI ---
NUM_ROWS = 2000
OUTPUT_FILE = 'dummy.csv'

# Database Koordinat Kota Besar Indonesia (Representative)
# Tier 1: Metropolitan Utama (Biaya Tinggi, Traffic Tinggi)
# Tier 2: Kota Besar (Biaya Menengah, Market Besar)
# Tier 3: Developing/Remote (Biaya Rendah, Market Niche)
CITIES_DB = [
    # JAWA
    {"city": "Jakarta Selatan", "prov": "DKI Jakarta", "lat": -6.2615, "lng": 106.8106, "tier": 1},
    {"city": "Jakarta Pusat", "prov": "DKI Jakarta", "lat": -6.1805, "lng": 106.8284, "tier": 1},
    {"city": "Tangerang Selatan", "prov": "Banten", "lat": -6.2886, "lng": 106.7179, "tier": 1},
    {"city": "Bandung", "prov": "Jawa Barat", "lat": -6.9175, "lng": 107.6191, "tier": 2},
    {"city": "Surabaya", "prov": "Jawa Timur", "lat": -7.2575, "lng": 112.7521, "tier": 1},
    {"city": "Semarang", "prov": "Jawa Tengah", "lat": -6.9667, "lng": 110.4167, "tier": 2},
    {"city": "Malang", "prov": "Jawa Timur", "lat": -7.9666, "lng": 112.6326, "tier": 3},
    {"city": "Yogyakarta", "prov": "DI Yogyakarta", "lat": -7.7955, "lng": 110.3695, "tier": 3},

    # SUMATERA
    {"city": "Medan", "prov": "Sumatera Utara", "lat": 3.5952, "lng": 98.6722, "tier": 2},
    {"city": "Palembang", "prov": "Sumatera Selatan", "lat": -2.9909, "lng": 104.7567, "tier": 2},
    {"city": "Batam", "prov": "Kep. Riau", "lat": 1.1301, "lng": 104.0529, "tier": 2},
    {"city": "Padang", "prov": "Sumatera Barat", "lat": -0.9471, "lng": 100.4172, "tier": 3},
    {"city": "Bandar Lampung", "prov": "Lampung", "lat": -5.3971, "lng": 105.2668, "tier": 3},

    # KALIMANTAN
    {"city": "Balikpapan", "prov": "Kalimantan Timur", "lat": -1.2379, "lng": 116.8529, "tier": 2},
    {"city": "Pontianak", "prov": "Kalimantan Barat", "lat": -0.0263, "lng": 109.3425, "tier": 3},
    {"city": "Samarinda", "prov": "Kalimantan Timur", "lat": -0.5022, "lng": 117.1536, "tier": 2},

    # SULAWESI & TIMUR
    {"city": "Makassar", "prov": "Sulawesi Selatan", "lat": -5.1477, "lng": 119.4327, "tier": 2},
    {"city": "Manado", "prov": "Sulawesi Utara", "lat": 1.4748, "lng": 124.8421, "tier": 3},
    {"city": "Denpasar", "prov": "Bali", "lat": -8.6705, "lng": 115.2126, "tier": 2},
    {"city": "Kupang", "prov": "NTT", "lat": -10.1772, "lng": 123.6070, "tier": 3},
    {"city": "Ambon", "prov": "Maluku", "lat": -3.6954, "lng": 128.1814, "tier": 3},
    {"city": "Jayapura", "prov": "Papua", "lat": -2.5916, "lng": 140.6690, "tier": 3},
]


def generate_indonesia_dataset():
    data = []
    street_names = [
        "Jend. Sudirman", "Gatot Subroto", "Ahmad Yani", "Diponegoro", "Imam Bonjol",
        "Gajah Mada", "Hayam Wuruk", "Merdeka", "Pahlawan", "Sisingamangaraja",
        "Pattimura", "Antasari", "Raden Saleh", "Cikini Raya", "Kemang", "Pasteur"
    ]

    print(f"🚀 Memulai generate {NUM_ROWS} data lokasi seluruh Indonesia...")

    for i in range(NUM_ROWS):
        # Pilih kota secara random (Weighted: Kota Tier 1 lebih banyak datanya)
        # Biar realistis, data Jakarta/Surabaya pasti lebih banyak dari Kupang
        base_city = random.choices(CITIES_DB, weights=[
            5, 5, 4, 4, 5, 4, 3, 3,  # Jawa weights (Higher)
            4, 3, 3, 2, 2,  # Sumatera weights
            3, 2, 2,  # Kalimantan weights
            3, 2, 4, 2, 2, 2  # Timur weights
        ], k=1)[0]

        # Random Jitter Koordinat (Agar menyebar dalam radius ~8km dari pusat kota)
        lat = base_city["lat"] + np.random.normal(0, 0.04)
        lng = base_city["lng"] + np.random.normal(0, 0.04)

        # --- LOGIC GENERATOR DATA ---
        tier_multiplier = {1: 1.5, 2: 1.2, 3: 0.9}
        factor = tier_multiplier[base_city["tier"]]

        # Income: Rata-rata gaji sekitar lokasi
        income_base = 4500000
        income = int(np.random.normal(income_base * factor, 1500000))
        income = max(2800000, income)  # Floor UMR

        # Traffic: Jumlah orang/kendaraan lewat
        traffic = int(np.random.normal(12000 * factor, 4000))
        traffic = max(2000, traffic)

        # Competitors: Jumlah saingan (Kota besar saingan makin banyak)
        competitors = int(np.random.normal(50 * factor, 20))
        competitors = max(0, competitors)

        # Rent: Harga sewa per tahun
        rent_base = 60000000
        rent = int(np.random.normal(rent_base * factor, 20000000))
        rent = max(15000000, rent)

        # --- ALGORITMA SKOR (SIMULASI AI) ---
        # Rumus: (Traffic + Income) - (Rent + Competitors)
        # Kita normalisasi biar jadi skala 0-100

        # Bobot
        w_traffic = 0.002
        w_income = 0.000005
        w_rent = 0.0000004
        w_comp = 0.3

        raw_score = (traffic * w_traffic) + (income * w_income) - (rent * w_rent) - (competitors * w_comp)

        # Adjust base score biar angkanya cantik (50-95)
        final_score = int(50 + raw_score + random.randint(-5, 10))
        final_score = min(99, max(10, final_score))  # Clamp 10-99

        # Tentukan Label
        if final_score >= 85:
            verdict = "Sangat Direkomendasikan ⭐"
            grade = "A"
        elif final_score >= 70:
            verdict = "Potensial ✅"
            grade = "B"
        elif final_score >= 55:
            verdict = "Cukup (Perlu Strategi) ⚠️"
            grade = "C"
        else:
            verdict = "Tidak Disarankan ❌"
            grade = "D"

        # Alamat Palsu tapi Realistis
        street = random.choice(street_names)
        no_jalan = random.randint(1, 200)
        address = f"Jl. {street} No. {no_jalan}, {base_city['city']}"

        data.append({
            "Location_ID": f"ID_{10000 + i}",
            "City": base_city["city"],
            "Province": base_city["prov"],
            "Address": address,
            "Latitude": round(lat, 6),
            "Longitude": round(lng, 6),
            "Avg_Income": income,
            "Traffic_Daily": traffic,
            "Competitors": competitors,
            "Rent_Per_Year": rent,
            "AI_Score": final_score,
            "Grade": grade,
            "Verdict": verdict
        })

    # Export ke CSV
    df = pd.DataFrame(data)
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"✅ SUKSES! File '{OUTPUT_FILE}' berisi {len(df)} baris telah dibuat.")
    print("Contoh Data:")
    print(df[['City', 'AI_Score', 'Verdict']].head())


if __name__ == "__main__":
    generate_indonesia_dataset()