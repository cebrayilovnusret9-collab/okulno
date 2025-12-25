from flask import Flask, jsonify, request
import csv
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Tüm CSV dosyalarını yükle
def load_all_csv():
    data = []
    
    # 7 dosya yükle (okulno1.csv ... okulno7.csv)
    for i in range(1, 8):
        filename = f'okulno{i}.csv'
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                next(reader)  # Başlığı atla
                
                for row in reader:
                    if len(row) >= 6:
                        data.append({
                            'id': row[0],
                            'tc_no': row[1],
                            'okul': row[2],
                            'isim': row[3],
                            'numara': row[4],
                            'durum': row[5]
                        })
    
    print(f"Toplam {len(data)} kayıt yüklendi")
    return data

okulno_data = load_all_csv()

@app.route('/')
def home():
    return "5M Okul No API"

@app.route('/f3system/api/okulno')
def search_okulno():
    tc = request.args.get('tc', '')
    isim = request.args.get('isim', '')
    okul = request.args.get('okul', '')
    durum = request.args.get('durum', '')
    limit = min(int(request.args.get('limit', 50)), 100)
    
    results = []
    
    for item in okulno_data:
        match = True
        
        if tc and tc not in item['tc_no']:
            match = False
        
        if isim and isim.upper() not in item['isim'].upper():
            match = False
            
        if okul and okul.upper() not in item['okul'].upper():
            match = False
            
        if durum and durum.upper() not in item['durum'].upper():
            match = False
        
        if match:
            results.append(item)
            if len(results) >= limit:
                break
    
    return jsonify({
        'aramalar': {
            'tc': tc,
            'isim': isim,
            'okul': okul,
            'durum': durum
        },
        'toplam_kayit': len(okulno_data),
        'bulunan': len(results),
        'sonuclar': results
    })

@app.route('/f3system/api/okulno/<tc_no>')
def get_by_tc(tc_no):
    for item in okulno_data:
        if item['tc_no'] == tc_no:
            return jsonify(item)
    
    return jsonify({'error': 'Kayıt bulunamadı'}), 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
