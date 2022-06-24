
---
# ds204ne.herokuapp.com/

## Running this project

Clone project về máy -> mở terminal -> di chuyển tới thư mục muốn lưu project

```
git clone https://github.com/thienthanh-09/source-ds204.git
```

Cài thư viện virtualenv vào môi trường Python

```
pip install virtualenv
```

Mở terminal -> di chuyển tới thư mục project vừa lưu về -> tạo môi trường ảo

```
virtualenv env
```

Kích hoạt môi trường ảo

```
env\Scripts\activate.bat
```

Cài đặt thư viện cho môi trường ảo

```
pip install -r requirements.txt
```

Kích hoạt database của project

```
py manage.py makemigrations
```

```
py manage.py migrate
```

Chạy project

```
py manage.py runserver
```

Mở trình duyệt -> gõ link http://127.0.0.1:8000/
