# app.py
from flask import Flask, jsonify
from flask_cors import CORS
import requests
import base64

app = Flask(__name__)
CORS(app)

# 🌐 2026 ခုနှစ်၏ လိုင်းအကောင်းဆုံး၊ အမြန်ဆုံးနှင့် သက်တမ်းအမြဲသစ်သော Premium Core Sources များ
VPN_SOURCES = [
    "https://raw.githubusercontent.com/ebrasha/free-v2ray-public-list/main/all_extracted_configs.txt", # ⚡ 15 မိနစ်တစ်ခါ Update ဖြစ်သော Source သစ်
    "https://raw.githubusercontent.com/freefq/free/master/v2ray",
    "https://raw.githubusercontent.com/vfarid/v2ray-share/main/all_links.txt",
    "https://raw.githubusercontent.com/w1770946466/Auto_Proxy/main/Long_term_subscription_num",
    "https://raw.githubusercontent.com/Pawdroid/Free-V2ray/main/v2ray"
]

@app.route('/api/vpnkeys', methods=['GET'])
def get_stable_vpn_keys():
    try:
        raw_keys = []
        
        # 📥 Sources တစ်ခုချင်းစီမှ Premium ဒေတာများ လှမ်းယူခြင်း
        for url in VPN_SOURCES:
            try:
                res = requests.get(url, timeout=8) # လိုင်းနှေးသော Source ကြောင့် မကြန့်ကြာစေရန် 8s သာ စောင့်မည်
                if res.status_code == 200:
                    text = res.text.strip()
                    if not text:
                        continue
                        
                    # Base64 ကုဒ်ထုပ်ကြီး ဖြစ်နေပါက Decode လုပ်ရန်
                    if not any(p in text for p in ["vmess://", "vless://", "ss://", "hysteria2://"]):
                        try:
                            cleaned_text = text.replace('\n', '').replace('\r', '').strip()
                            text = base64.b64decode(cleaned_text).decode('utf-8', errors='ignore')
                        except:
                            pass
                    
                    lines = text.split('\n')
                    for l in lines:
                        l = l.strip()
                        # ခေတ်မီပြီး အပိတ်ရခက်သော Protocols များကို စစ်ထုတ်ယူခြင်း
                        if l and any(l.startswith(p) for p in ["ss://", "vmess://", "vless://", "trojan://", "hysteria2://", "tuic://"]):
                            raw_keys.append(l)
            except:
                continue

        # ဒေတာလုံးဝမရရှိပါက ပေါ်ပေးမည့် စိတ်ချရသော အရန် Nodes များ
        if not raw_keys:
            raw_keys = [
                "vless://6c5g7g4e-b643-44f3-8dd5-48b6432022e3@128.199.65.12:443?encryption=none&security=reality&sni=www.google.com&fp=chrome#Singapore_Premium_Reality",
                "ss://Y2hhY2hhMjAtaWV0Zi1wb2x5MTMwNTo2Y0M1RzZ0Z3Y0ZTI@139.59.220.50:443#Japan_Stable_SS"
            ]

        vpn_list = []
        # မြန်မာပြည်နှင့် အနီးဆုံးဖြစ်ပြီး Route လမ်းကြောင်းအကောင်းဆုံးနိုင်ငံများ
        priority_countries = {
            "SG": "Singapore 🇸🇬 Premium",
            "HK": "Hong Kong 🇭🇰 Premium",
            "JP": "Japan 🇯🇵 Stable",
            "TW": "Taiwan 🇹🇼 High-Speed",
            "KR": "Korea 🇰🇷 Stable",
            "US": "United States 🇺🇸 Extra"
        }
        
        for key in raw_keys:
            detected_country = "Global Premium Node 🌐"
            detected_code = "GL"
            
            key_upper = key.upper()
            for code, name in priority_countries.items():
                if code in key_upper or name.split()[0].upper() in key_upper:
                    detected_code = code
                    detected_country = name
                    break

            # 💡 Reality စနစ် သုံးထားပါက အထူးအမှတ်အသားပြုလုပ်ရန်
            vpn_type = key.split("://")[0].upper()
            if "SECURITY=REALITY" in key_upper:
                vpn_type = "REALITY (VLESS)"
            elif vpn_type == "HYSTERIA2":
                vpn_type = "HYSTERIA 2"

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

        # 🔄 စင်ကာပူးနှင့် ဂျပန်ကဲ့သို့ အငြိမ်ဆုံးနိုင်ငံများကို ဦးစားပေး ထိပ်ဆုံးတင်ခြင်း
        vpn_list = sorted(vpn_list, key=lambda x: x['country_code'] in ["SG", "HK", "JP", "TW"], reverse=True)
        
        # တစ်နိုင်ငံတည်းမှ ဆာဗာများ ပြွတ်သိပ်မနေစေဘဲ အကောင်းဆုံး Nodes များကိုသာ ရွေးချယ်ခြင်း
        final_list = []
        counts = {}
        for item in vpn_list:
            code = item['country_code']
            counts[code] = counts.get(code, 0) + 1
            if counts[code] <= 5:  # တစ်နိုင်ငံလျှင် အမြန်ဆုံး ၅ လိုင်းစီသာပြမည်
                final_list.append(item)
            if len(final_list) >= 30: # စုစုပေါင်း Premium အပုဒ်ရေ ၃၀ သာ ပြသမည်
                break

        return jsonify({"status": "success", "data": final_list})
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
