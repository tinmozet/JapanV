# app.py
from flask import Flask, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app) # Frontend က လှမ်းခေါ်ခွင့်ပြုရန်

VPNGATE_API_URL = "http://www.vpngate.net/api/iphone/"

@app.route('/api/vpnkeys', methods=['GET'])
def get_vpn_keys():
    try:
        # VPN Gate ဆီကနေ အကောင့် Keys ဒေတာများ Fetch လုပ်ခြင်း (Timeout 15 စက္ကန့်)
        response = requests.get(VPNGATE_API_URL, timeout=15)
        text_data = response.text
        
        lines = text_data.split('\n')
        vpn_list = []
        
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
            country_long = parts[5]
            country_short = parts[6]
            vpn_config_base64 = parts[14].strip()
            
            # ဒေတာမပြည့်စုံလျှင် ကျော်သွားရန်
            if not vpn_config_base64 or len(vpn_config_base64) < 100:
                continue

            # 💡 [အရေးကြီးဆုံး ပြင်ဆင်ချက်] - Base64 ကုဒ်ကို Decode လုပ်ပြီး အတွင်းပိုင်းကို စစ်ဆေးခြင်း
            try:
                import base64
                decoded_text = base64.b64decode(vpn_config_base64).decode('utf-8', errors='ignore')
                
                # မြန်မာပြည်တွင် UDP Port များကို ပိတ်ထားသဖြင့် "proto tcp" (TCP စနစ်) သုံးထားသော ကီးများကိုသာ ယူမည်
                if "proto tcp" not in decoded_text.lower():
                    continue # UDP ဖြစ်ပါက ချန်လှပ်ခဲ့ပြီး နောက်တစ်လိုင်းသို့ သွားမည်
                    
            except Exception:
                continue # Base64 ဖတ်မရပါက ကျော်သွားရန်

            vpn_list.append({
                "host": host_name,
                "ip": ip_address,
                "ping": ping,
                "speed": f"{round(speed / 1000000, 2)} Mbps" if speed > 0 else "N/A",
                "speed_raw": speed,
                "country": country_long,
                "country_code": country_short,
                "config_b64": vpn_config_base64
            })
        
        # ⚡ လိုင်းအမြန်ဆုံး Server များကို အရင်စီခြင်း
        sorted_vpns = sorted(vpn_list, key=lambda x: x['speed_raw'], reverse=True)

        # 🌍 နိုင်ငံစုံ စုံစုံလင်လင် ပါဝင်စေရန် စစ်ထုတ်မည့် စနစ် (Country-Based Round Robin)
        final_vpn_list = []
        seen_countries = {}

        for vpn in sorted_vpns:
            c_code = vpn['country_code']
            if c_code not in seen_countries:
                seen_countries[c_code] = 0
            
            # နိုင်ငံတစ်ခုတည်းက ဆာဗာတွေချည်းပဲ အများကြီး မပြွတ်သိပ်နေအောင် 
            # တစ်နိုင်ငံလျှင် အကောင်းဆုံး ဆာဗာ ၃ ခု ထက်ပိုမယူဘဲ ကန့်သတ်ခြင်း (ဒါမှ နိုင်ငံစုံ စုံလင်စွာ ပေါ်လာပါမည်)
            if seen_countries[c_code] < 3:
                final_vpn_list.append(vpn)
                seen_countries[c_code] += 1
                
            # စုစုပေါင်း ကီးအခု ၂၀ ပြည့်ပါက ရပ်တန့်မည်
            if len(final_vpn_list) >= 20:
                break

        # ဒေတာ သန့်ရှင်းရေးအတွက် speed_raw ကို ပြန်ဖျက်ခြင်း
        for v in final_vpn_list:
            v.pop('speed_raw', None)

        return jsonify({"status": "success", "data": final_vpn_list})
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
