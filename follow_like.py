import os
import subprocess
import requests
from datetime import datetime

# Thiết lập thư mục log
log_dir = os.path.join(os.path.dirname(__file__), 'log')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'follow_client.log')

def log(message):
    """Ghi log vào console và file"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"{timestamp} - {message}")
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"{timestamp} - {message}\n")

def get_device_id():
    """Lấy device_id của thiết bị Android hiện tại"""
    try:
        # Sử dụng getprop để lấy ro.serialno
        cmd = "getprop ro.serialno"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            device_id = result.stdout.strip()
            if device_id:
                #log(f"Lấy được device_id: {device_id}")
                return device_id
            else:
                log("Không lấy được device_id từ getprop")
                return "unknown_device"
        else:
            log(f"Lỗi khi lấy device_id: {result.stderr}")
            return "unknown_device"
    except Exception as e:
        log(f"Lỗi khi lấy device_id: {str(e)}")
        return "unknown_device"

def send_follow_request(url='http://10.0.0.17:8000/follow'):
    """Gửi yêu cầu Follow tới PC và nhận kết quả"""
    try:
        device_id = get_device_id()
        payload = {'device_id': device_id, 'task': 'FOLLOW'}
        #log(f"Gửi yêu cầu tới {url} với payload: {payload}")
        response = requests.post(url, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            status = result.get('status')
            result_msg = result.get('result')
            #log(f"Nhận phản hồi từ server: {status} - {result_msg}")
            return result_msg
        else:
            log(f"Lỗi khi gửi yêu cầu tới server: HTTP {response.status_code}")
            return f"Error: HTTP {response.status_code}"
    except requests.exceptions.Timeout:
        log(f"Lỗi: Yêu cầu tới {url} bị timeout sau 60 giây")
        return "Error: Request timed out"
    except requests.exceptions.ConnectionError:
        log(f"Lỗi: Không thể kết nối tới {url}. Kiểm tra mạng hoặc server")
        return "Error: Connection failed"
    except Exception as e:
        log(f"Lỗi khi gửi yêu cầu tới server: {str(e)}")
        return f"Error: {str(e)}"

if __name__ == "__main__":
    result = send_follow_request()
    print(result)
