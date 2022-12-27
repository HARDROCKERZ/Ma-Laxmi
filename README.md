
# Ma Laxmi

#### Ecommerce build using Django - Model View Template.
- This project was build for a client as part of internship.
- Code base is made open source
- Using Django inbuilt functionality many features are implemented
- Include payment gateway



## 🛠 Technologies
**Client:** Django, HTML, CSS, JSON, Javascript

**Server:** Django, Railway Hosting 



## Screenshots

### Home page
![App Screenshot](https://i.postimg.cc/kXNLtP4s/HomePage.png)

### Product view
![App Screenshot](https://i.postimg.cc/wThKnxmV/Product.png)

### Payment page
![App Screenshot](https://i.postimg.cc/FKXYNHWH/Payment.png)

## Run Locally

To deploy this project run

#### Setup python virtual environment
```
https://docs.python.org/3/library/venv.html
```

#### Activate environment
```
source env/bin/activate
```

#### Install requirements
```
pip3 install -r requirements.txt
```

#### Before running make changes in settings.py
```
provide credential inside in order to make it functional
```

#### To run on local host
```
python3 manage.py runserver
```
## Environment Variables

To run this project, you will need to add the following environment variables to your .env file
#### Generate secret online using csrf key generator
`SECRET_KEY`

#### Set host to 'smtp.gmail.com'
`EMAIL_HOST`

#### Set port to '587'
`EMAIL_PORT`

#### Provide email address inorder to run email functionality
`EMAIL_HOST_USER`

#### Password for the same
`EMAIL_HOST_PASSWORD`

#### Set it to 'True'
`EMAIL_USE_TLS`
## Demo

https://ma-laxmi.up.railway.app/


## Features

- Multiple Admin
- Paypal & Cod payment gateway
- Email verification while registration
- Responsive for mobile web view
- Bill receipt is generated for every order

