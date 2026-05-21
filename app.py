# app.py
from flask import Flask, jsonify
from flask_cors import CORS
import requests
import base64

app = Flask(__name__)
CORS(app)

# 🌐 VPN Gate ရဲ့ တရားဝင် API နှင့် ပိတ်ဆို့မှုကို ကျော်ဖြတ်နိုင်သော အရန် Mirror API လင့်ခ်များ
VPNGATE_API_URLS = [
    "http://www.vpngate.net/api/iphone/",
    "https://www.vpngate.net/api/iphone/",
    "http://130.158.6.132:80/api/iphone/", # VPN Gate မူရင်း IP တိုက်ရိုက်လင့်ခ်
    "http://130.158.6.133:80/api/iphone/"
]

@app.route('/api/vpnkeys', methods=['GET'])
def get_stable_openvpn_keys():
    text_data = None
    
    # 📥 လင့်ခ်တစ်ခု ပျက်နေလျှင် နောက်တစ်ခုမှ မဖြစ်မနေ ဒေတာဆွဲယူမည့် စနစ်
    for url in VPNGATE_API_URLS:
        try:
            response = requests.get(url, timeout=8)
            if response.status_code == 200 and "HostName" in response.text:
                text_data = response.text
                break # ဒေတာရပြီဆိုလျှင် Loop ကို ရပ်မည်
        except:
            continue

    # အကယ်၍ API အားလုံး ချိတ်မရပါက အောက်ပါ Static အရန် ကုဒ်ကို ချပြမည် (အက်ပ် အမြဲအလုပ်လုပ်စေရန်)
    if not text_data:
        return jsonify({
            "status": "success", 
            "data": [
                {
                    "host": "public-vpn-backup",
                    "ip": "128.199.65.12",
                    "ping": "45",
                    "speed": "25.5 Mbps",
                    "country": "Singapore 🇸🇬 Premium",
                    "country_code": "SG",
                    "config_b64": "Y2xpZW50Cl9fX0JBR0lBTl9ORVdfX18=" # Dummy သို့မဟုတ် ဆရာ့ကိုယ်ပိုင် Config ထည့်နိုင်သည်
                }
            ]
        })
        
    try:
        lines = text_data.split('\n')
        vpn_list = []
        
        # မြန်မာပြည်နှင့် အဆင်ပြေဆုံး အာရှပစိဖိတ်နိုင်ငံများ
        allowed_countries = {
            "SG": "Singapore 🇸🇬",
            "JP": "Japan 🇯🇵",
            "KR": "Korea 🇰🇷",
            "TH": "Thailand 🇹🇭",
            "TW": "Taiwan 🇹🇼"
        }
        
        for line in lines:
            line = line.strip()
            if line.startswith('*') or line.startswith('#') or not line:
                continue
                
            parts = line.split(',')
            if len(parts) < 15:
                continue
                
            host_name = parts[0]
            ip_address = parts[1]
            ping = parts[3]
            speed = int(parts[4]) if parts[4].isdigit() else 0
            country_short = parts[6].upper()
            vpn_config_base64 = parts[14].strip()
            
            if not vpn_config_base64 or len(vpn_config_base64) < 100:
                continue

            # 💡 နိုင်ငံ စစ်ထုတ်ခြင်း
            if country_short not in allowed_countries:
                continue 

            # 💡 မြန်မာပြည်အတွက် TCP စနစ်သီးသန့်ကို စစ်ထုတ်ခြင်း (Port ကို ခပ်ချောင်ချောင်ပဲ စစ်တော့မည်)
            try:
                decoded_text = base64.b64decode(vpn_config_base64).decode('utf-8', errors='ignore')
                if "proto tcp" not in decoded_text.lower():
                    continue # UDP များကို ဖယ်ထုတ်မည်
            except:
                continue

            vpn_list.append({
                "host": host_name,
                "ip": ip_address,
                "ping": ping,
                "speed": f"{round(speed / 1000000, 2)} Mbps" if speed > 0 else "N/A",
                "speed_raw": speed,
                "country": allowed_countries[country_short],
                "country_code": country_short,
                "config_b64": vpn_config_base64
            })
        
        # Speed အလိုက် အစဉ်စီခြင်း
        sorted_vpns = sorted(vpn_list, key=lambda x: x['speed_raw'], reverse=True)

        # မျှတစွာ ဖြန့်ဝေပြသခြင်း စနစ်
        final_list = []
        counts = {}
        for vpn in sorted_vpns:
            code = vpn['country_code']
            counts[code] = counts.get(code, 0) + 1
            if counts[code] <= 5: # တစ်နိုင်ငံလျှင် အကောင်းဆုံး ၅ ခုစီပြမည်
                final_list.append(vpn)
            if len(final_list) >= 20:
                break

        for v in final_list:
            v.pop('speed_raw', None)

        return jsonify({"status": "success", "data": final_list})
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
