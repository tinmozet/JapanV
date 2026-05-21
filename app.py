# app.py
from flask import Flask, jsonify, Response
from flask_cors import CORS
import requests
import base64

app = Flask(__name__)
CORS(app) # Frontend ကနေ လှမ်းခေါ်လို့ရအောင် CORS ဖွင့်ပေးခြင်း

VPNGATE_API_URL = "http://www.vpngate.net/api/iphone/"

@app.route('/api/vpnkeys', methods=['GET'])
def get_vpn_keys():
    try:
        response = requests.get(VPNGATE_API_URL, timeout=10)
        text_data = response.text
        
        # VPN Gate ရဲ့ ဒေတာတွေကို လိုင်းချင်းစီ ခွဲထုတ်ခြင်း
        lines = text_data.split('\n')
        
        vpn_list = []
        for line in lines:
            if line.startswith('*') or line.startswith('#') or not line.strip():
                continue
                
            parts = line.split(',')
            if len(parts) < 15:
                continue
                
            # ဒေတာများကို သပ်သပ်ရပ်ရပ် စစ်ထုတ်ယူခြင်း
            host_name = parts[0]
            ip_address = parts[1]
            score = int(parts[2])
            ping = parts[3]
            speed = int(parts[4]) if parts[4].isdigit() else 0
            country_long = parts[5]
            country_short = parts[6]
            vpn_config_base64 = parts[14] # OpenVPN Config သော့ချက်
            
            # မြန်မာပြည်ကနေ သုံးရင် အဆင်ပြေဆုံးဖြစ်မယ့် ဂျပန်၊ ကိုရီးယား၊ စင်ကာပူး တို့ကို ဦးစားပေးပြရန်
            vpn_list.append({
                "host": host_name,
                "ip": ip_address,
                "ping": ping,
                "speed": f"{round(speed / 1000000, 2)} Mbps" if speed > 0 else "N/A",
                "country": country_long,
                "country_code": country_short,
                "config_b64": vpn_config_base64
            })
        
        # Speed အမြန်ဆုံး Server တွေကို ထိပ်ကစီပေးခြင်း
        vpn_list = sorted(vpn_list, key=lambda x: x['speed'], reverse=True)[:20]
        return jsonify({"status": "success", "data": vpn_list})
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
