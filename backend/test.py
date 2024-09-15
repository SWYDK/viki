import requests

API_KEY = '6ed8edbb18597fcb955280f28cf83ec4'
USER_TOKEN = '06b873005a509ae9df6818c801310a2d'
BASE_URL = 'https://api.yclients.com/api/v1'

def get_employees(api_key, user_token):
    url = f"https://api.yclients.com/api/v1/records/440555"
    headers = {
        'Authorization': 'Bearer 83uag8prg689533sw7cx, User 06b873005a509ae9df6818c801310a2d',
        'Accept': 'application/vnd.yclients.v2+json',
        'Content-Type': 'application/json',
    }
    data = {
        "staff_id": 0,
        "services": [
            
        ],
        "client": {
            "phone": "79169999900",
            "name": "Дмитрий",
            "surname": "",
            "patronymic": "",
            "email": "d@yclients.com"
        },
        "datetime": "2024-09-03 17:00:00",
        "seance_length": 3600,
        "comment": "тестовая запись!",
        "sms_remain_hours": 6,
        "email_remain_hours": 24,
        "attendance": 1,
        "api_id": "777",
        "custom_color": "f44336",
        "record_labels": [
            "67345",
            "104474"
        ],
        
}
    response = requests.post(url, json=data, headers=headers)
    response.raise_for_status()
    return response.json()

if __name__ == "__main__":
    employees = get_employees(API_KEY, USER_TOKEN)
    print(f"{employees}")
      

