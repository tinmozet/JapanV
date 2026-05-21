# app.py
from flask import Flask, jsonify
from flask_cors import CORS
import requests
import base64

app = Flask(__name__)
CORS(app)

# 🌐 အင်တာနက်ပေါ်မှ အချိန်နဲ့တပြေးညီ Update ဖြစ်နေသော Premium VPN Node Sources များ
VPN_SOURCES = [
    "https://raw.githubusercontent.com/freefq/free/master/v2ray",
    "https://raw.githubusercontent.com/vfarid/v2ray-share/main/all_links.txt",
    "https://raw.githubusercontent.com/Pawdroid/Free-V2ray/main/v2ray"
]

@app.route('/api/vpnkeys', methods=['GET'])
def get_stable_vpn_keys():
    try:
        raw_keys = []
        
        # 📥 ဇစ်မြစ် Website များဆီကနေ ဒေတာ လှမ်းဆွဲခြင်း
        for url in VPN_SOURCES:
            try:
                res = requests.get(url, timeout=12)
                if res.status_code == 200:
                    text = res.text
                    
                    # ဒေတာက Base64 စာသားထုပ်ကြီး ဖြစ်နေပါက Decode လုပ်ရန်
                    if "vmess://" not in text and "ss://" not in text and "vless://" not in text:
                        try:
                            text = base64.b64decode(text.strip()).decode('utf-8', errors='ignore')
                        except:
                            pass
                    
                    lines = text.split('\n')
                    raw_keys.extend([l.strip() for l in lines if l.strip()])
            except:
                continue

        vpn_list = []
        # 🇲🇲 မြန်မာပြည်နှင့် ပင်လယ်ရေအောက်ကေဘယ် တိုက်ရိုက်ချိတ်ဆက်ထားပြီး Ping အနည်းဆုံး နိုင်ငံများ
        priority_countries = {
            "SG": "Singapore 🇸🇬",
            "HK": "Hong Kong 🇭🇰",
            "JP": "Japan 🇯🇵",
            "TW": "Taiwan 🇹🇼",
            "KR": "Korea 🇰🇷",
            "US": "United States 🇺🇸"
        }
        
        # ဒေတာများကို တစ်ခုချင်းစီ သန့်စင်စစ်ထုတ်ခြင်း
        for key in raw_keys:
            if not (key.startswith("ss://") or key.startswith("vmess://") or key.startswith("vless://") or key.startswith("trojan://")):
                continue

            # နိုင်ငံ ခွဲခြားသတ်မှတ်ခြင်း Logic
            detected_country = "Global Server 🌐"
            detected_code = "GL"
            
            key_upper = key.upper()
            for code, name in priority_countries.items():
                if code in key_upper or name.split()[0].upper() in key_upper:
                    detected_code = code
                    detected_country = name
                    break

            # ကီး အမျိုးအစား ခွဲခြားခြင်း (ဥပမာ - VMESS, VLESS, SS)
            vpn_type = key.split("://")[0].upper()
            
            # Frontend ထဲ သွားတဲ့အခါ ကုဒ်မပဲ့အောင် Base64 အဖြစ် ခေတ္တပြောင်းသိမ်းခြင်း
            encoded_key = base64.b64encode(key.encode('utf-8')).decode('utf-8')
            
            vpn_list.append({
                "country": detected_country,
                "country_code": detected_code,
                "type": vpn_type,
                "config_b64": encoded_key
            })

        # 🔄 Priority နိုင်ငံများကို ထိပ်ဆုံးကပြပြီး နိုင်ငံစုံမျှအောင် အပုဒ် ၂၅ သာ စစ်ထုတ်ယူခြင်း
        vpn_list = sorted(vpn_list, key=lambda x: x['country_code'] in priority_countries.keys(), reverse=True)
        
        # တစ်နိုင်ငံတည်း ချည်းပဲ ပြွတ်သိပ်မနေအောင် ဒေတာကို ခပ်ကျဲကျဲ စစ်ထုတ်ခြင်း
        final_list = []
        counts = {}
        for item in vpn_list:
            code = item['country_code']
            counts[code] = counts.get(code, 0) + 1
            if counts[code] <= 4: # တစ်နိုင်ငံလျှင် အများဆုံး ၄ လိုင်းစီသာ ပြမည်
                final_list.append(item)
            if len(final_list) >= 25:
                break

        return jsonify({"status": "success", "data": final_list})
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
