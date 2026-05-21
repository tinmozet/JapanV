# app.py
from flask import Flask, jsonify
from flask_cors import CORS
import requests
import base64

app = Flask(__name__)
CORS(app)

VPNGATE_API_URL = "http://www.vpngate.net/api/iphone/"

@app.route('/api/vpnkeys', methods=['GET'])
def get_stable_openvpn_keys():
    try:
        response = requests.get(VPNGATE_API_URL, timeout=12)
        text_data = response.text
        
        lines = text_data.split('\n')
        vpn_list = []
        
        # 🇲🇲 မြန်မာပြည်နှင့် အနီးဆုံးဖြစ်ပြီး လိုင်းအငြိမ်ဆုံး OpenVPN နိုင်ငံများ
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

            # 💡 [မြန်မာပြည်အတွက် အဓိက သော့ချက်] - နိုင်ငံနှင့် TCP စနစ်ကိုသာ စစ်ထုတ်ခြင်း
            if country_short not in allowed_countries:
                continue # သတ်မှတ်နိုင်ငံမဟုတ်ပါက ကျော်မည်

            try:
                decoded_text = base64.b64decode(vpn_config_base64).decode('utf-8', errors='ignore')
                
                # အော်ပရေတာများ ပိတ်ရခက်ခဲသော TCP စနစ်ဖြစ်ပြီး၊ Port 443 သို့မဟုတ် 995 ဖြစ်သော ကီးများကိုသာ ရွေးမည်
                if "proto tcp" not in decoded_text.lower():
                    continue
                if not any(p in decoded_text for p in ["port 443", "port 995", "port 1195", "port 53"]):
                    continue
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
        
        # လိုင်းအမြန်ဆုံးဆာဗာများကို အရင်စီခြင်း
        sorted_vpns = sorted(vpn_list, key=lambda x: x['speed_raw'], reverse=True)

        # တစ်နိုင်ငံတည်းက ဆာဗာတွေချည်းပဲ မပြွတ်သိပ်နေအောင် စစ်ထုတ်ခြင်း
        final_list = []
        counts = {}
        for vpn in sorted_vpns:
            code = vpn['country_code']
            counts[code] = counts.get(code, 0) + 1
            if counts[code] <= 4: # တစ်နိုင်ငံလျှင် အကောင်းဆုံးဆာဗာ ၄ ခုစီသာပြမည်
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
