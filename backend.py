from flask import Flask, jsonify, request
import pandas as pd
import glob
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Kanal bilgileri
KANAL_BILGILERI = {
    "kanal": "@f3system",
    "kurucu": "@sukazatkinis",
    "api": "okulno"
}

# CSV dosyalarını yükle
def load_csv_data():
    try:
        csv_files = sorted(glob.glob("okulno*.csv"))
        if not csv_files:
            return pd.DataFrame()
        
        dfs = []
        for file in csv_files:
            df = pd.read_csv(file, header=None, 
                           encoding='utf-8',
                           names=['sira_no', 'tc_kimlik', 'ad', 'soyad', 'okul_no', 'durum'])
            dfs.append(df)
        
        return pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()
    except:
        return pd.DataFrame()

# Tek endpoint - tüm aramalar
@app.route('/f3/api/okulno', methods=['GET'])
def search_ogrenci():
    # Tüm parametreleri al
    tc = request.args.get('tc')
    ad = request.args.get('ad')
    soyad = request.args.get('soyad')
    okulno = request.args.get('okulno')
    durum = request.args.get('durum')
    
    # Veriyi yükle
    df = load_csv_data()
    
    if df.empty:
        return jsonify({
            **KANAL_BILGILERI,
            "status": "error",
            "message": "Veri bulunamadı"
        }), 404
    
    # Filtreleme
    filtered_df = df.copy()
    
    # TC'ye göre filtrele
    if tc:
        filtered_df = filtered_df[filtered_df['tc_kimlik'].astype(str).str.contains(str(tc), na=False)]
    
    # Ada göre filtrele (case-insensitive)
    if ad:
        filtered_df = filtered_df[filtered_df['ad'].str.contains(ad, case=False, na=False)]
    
    # Soyada göre filtrele
    if soyad:
        filtered_df = filtered_df[filtered_df['soyad'].str.contains(soyad, case=False, na=False)]
    
    # Okul numarasına göre filtrele
    if okulno:
        filtered_df = filtered_df[filtered_df['okul_no'].astype(str).str.contains(str(okulno), na=False)]
    
    # Duruma göre filtrele
    if durum:
        filtered_df = filtered_df[filtered_df['durum'].str.contains(durum, case=False, na=False)]
    
    # Sonuçları hazırla
    results = filtered_df.to_dict('records')
    
    return jsonify({
        **KANAL_BILGILERI,
        "status": "success",
        "query": {
            "tc": tc,
            "ad": ad,
            "soyad": soyad,
            "okulno": okulno,
            "durum": durum
        },
        "total_results": len(results),
        "results": results
    })

# Sadece kanal bilgileri için ana sayfa
@app.route('/')
def home():
    return jsonify(KANAL_BILGILERI)

# API çalıştırma
if __name__ == '__main__':
    print("📡 F3 System API başlatılıyor...")
    print(f"🔗 Kanal: {KANAL_BILGILERI['kanal']}")
    print(f"👤 Kurucu: {KANAL_BILGILERI['kurucu']}")
    print("🌐 Endpoint: /f3/api/okulno")
    print("\n✅ API hazır! Kullanım örnekleri:")
    print("   /f3/api/okulno?ad=GAZAL")
    print("   /f3/api/okulno?tc=19007791262")
    print("   /f3/api/okulno?soyad=YILMAZ")
    print("   /f3/api/okulno?okulno=776")
    print("   /f3/api/okulno?durum=Mezun")
    print("\n🚀 Sunucu başlatılıyor...")
    app.run(debug=True, host='0.0.0.0', port=5000)
