# app.py
from flask import Flask, jsonify
from flask_cors import CORS
import requests
import base64

app = Flask(__name__)
CORS(app)

# 🌐 ပိုမိုစိတ်ချရပြီး ဒေတာအမြဲရှိသော ကမ္ဘာကျော် Free V2Ray/Shadowsocks Sources များ
VPN_SOURCES = [
    "https://raw.githubusercontent.com/freefq/free/master/v2ray",
    "https://raw.githubusercontent.com/vfarid/v2ray-share/main/all_links.txt",
    "https://raw.githubusercontent.com/w1770946466/Auto_Proxy/main/Long_term_subscription_num",
    "https://raw.githubusercontent.com/tbbatbb/Proxy/master/dist/v2ray.config"
]

@app.route('/api/vpnkeys', methods=['GET'])
def get_stable_vpn_keys():
    try:
        raw_keys = []
        
        # 📥 Sources တစ်ခုချင်းစီကနေ ဒေတာ ဆွဲယူခြင်း
        for url in VPN_SOURCES:
            try:
                # Timeout ကို 10 စက္ကန့်ထားပြီး လိုင်းမကောင်းသော Source ကြောင့် ကြန့်ကြာမှုမရှိအောင် လုပ်ခြင်း
                res = requests.get(url, timeout=10)
                if res.status_code == 200:
                    text = res.text.strip()
                    if not text:
                        continue
                        
                    # ဒေတာက Base64 စာသားထုပ်ကြီး ဖြစ်နေပါက ဖြန့်ချခြင်း
                    if "vmess://" not in text and "ss://" not in text and "vless://" not in text:
                        try:
                            # နေရာလွတ်များနှင့် စာကြောင်းအသစ်များကို ရှင်းလင်းပြီးမှ Decode လုပ်ခြင်း
                            cleaned_text = text.replace('\n', '').replace('\r', '').strip()
                            text = base64.b64decode(cleaned_text).decode('utf-8', errors='ignore')
                        except:
                            pass
                    
                    lines = text.split('\n')
                    for l in lines:
                        l = l.strip()
                        if l and any(l.startswith(p) for p in ["ss://", "vmess://", "vless://", "trojan://"]):
                            raw_keys.append(l)
            except:
                continue

        # ဒေတာ လုံးဝမရရှိပါက အောက်ပါ Static အရန် Nodes များကို ပြပေးရန် (App မရဏဖြစ်ခြင်းမှ ကာကွယ်ရန်)
        if not raw_keys:
            raw_keys = [
                "ss://Y2hhY2hhMjAtaWV0Zi1wb2x5MTMwNTo2Y0M1RzZ0Z3Y0ZTI@128.199.65.12:443#Singapore_Backup_SS",
                "ss://Y2hhY2hhMjAtaWV0Zi1wb2x5MTMwNTo2Y0M1RzZ0Z3Y0ZTI@139.59.220.50:443#Japan_Backup_SS"
            ]

        vpn_list = []
        priority_countries = {
            "SG": "Singapore 🇸🇬",
            "HK": "Hong Kong 🇭🇰",
            "JP": "Japan 🇯🇵",
            "TW": "Taiwan 🇹🇼",
            "KR": "Korea 🇰🇷",
            "US": "United States 🇺🇸"
        }
        
        for key in raw_keys:
            detected_country = "Global Premium Server 🌐"
            detected_code = "GL"
            
            key_upper = key.upper()
            for code, name in priority_countries.items():
                if code in key_upper or name.split()[0].upper() in key_upper:
                    detected_code = code
                    detected_country = name
                    break

            vpn_type = key.split("://")[0].upper()
            
            try:
                encoded_key = base64.b64encode(key.encode('utf-8')).decode('utf-8')
                vpn_list.append({
                    "country": detected_country,
                    "country_code": detected_code,
                    "type": vpn_type,
                    "config_b64": encoded_key
                })
            except:
                continue

        # 🔄 စင်ကာပူး၊ ဂျပန် စသည့် နိုင်ငံများကို ထိပ်ဆုံးသို့ ပို့ပေးခြင်း
        vpn_list = sorted(vpn_list, key=lambda x: x['country_code'] in priority_countries.keys(), reverse=True)
        
        # တစ်နိုင်ငံတည်း ပြွတ်သိပ်မနေအောင် ခွဲထုတ်ခြင်း
        final_list = []
        counts = {}
        for item in vpn_list:
            code = item['country_code']
            counts[code] = counts.get(code, 0) + 1
            if counts[code] <= 5:  # တစ်နိုင်ငံလျှင် အများဆုံး ၅ လိုင်းစီပြမည်
                final_list.append(item)
            if len(final_list) >= 30: # အပုဒ်ရေ ၃၀ အထိ တိုးမြှင့်ပြသမည်
                break

        return jsonify({"status": "success", "data": final_list})
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
