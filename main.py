from fastapi import FastAPI,HTTPException,Depends,Header
import secrets
from pwdlib import PasswordHash
from pydantic import BaseModel,Field
from fastapi.security import HTTPBearer

app = FastAPI()

data = {'AI Conference':100,
        'Music Festival':250,
        'Python Workshop':30}
reservation_number = 0
book = []
id_with_confirm_code = []
security1 = HTTPBearer(auto_error=False)

@app.post('/reservations/event_name/tickets')
def Ticket_Reservation(event_name:str,tickets:int,customer_name:str,check=Depends(security1),authorization: str | None = Header(default=None)):
    global reservation_number

    if authorization is not None and check is None:
        raise HTTPException(status_code=401, detail= 'Invalid Authorization header')

    certified_user = None
    if check is not None:
        found = False
        for item in confirm_codes_login:
            if check.credentials == item[0]:
                certified_user = item[1]
                found = True
        if found == False:
            raise HTTPException(status_code=401, detail= 'Invalid access token')

    if customer_name.strip() == '' or customer_name.strip().isdigit():
        raise HTTPException(status_code=400, detail='Invalid name')

    for key in data.keys():
        if event_name.lower().replace(' ','') == key.lower().replace(' ',''):
            if tickets > 0 :
                if data[key]>=tickets:
                    reservation_number += 1
                    data[key] -= tickets
                    book.append((reservation_number,customer_name,key,tickets))

                    if certified_user is not None:
                        id_with_reservations[certified_user] = id_with_reservations.get(certified_user,[]) + [reservation_number]

                    confirm_code = secrets.token_urlsafe(32)
                    id_with_confirm_code.append({reservation_number:confirm_code})



                    return {'Reservation id': reservation_number,
                            'Customer name': customer_name, 'Event_name':key,
                             'Tickets':tickets,
                            'Confirm code':confirm_code}
                else:
                    raise HTTPException(status_code = 409,
                                        detail=f'Only {data[key]} available for the {key}')

            else:
                raise HTTPException(status_code=400, detail ='Please reserve at least one ticket')
    raise HTTPException(status_code=404, detail='No such event available at the moment')




@app.get('/reservations/{event_name}/tickets')
def Tickets_available(event_name:str):
    for key in data.keys():
        if event_name.lower().replace(' ','') == key.lower().replace(' ',''):
            return {'Event name': key,
            'Tickets': data[key]}
    raise HTTPException(status_code=404, detail='No such event available at the moment')


security = HTTPBearer()

def check_credentials(check=Depends(security)):

    for item in confirm_codes_login:
        if check.credentials == item[0]:
            return item[1]

    raise HTTPException(status_code=401, detail='Invalid access token')


cancel_book = []

@app.post('/cancellations/event_name')
def Tickets_cancellation(event_name: str, reservation_id: int,
                         certified_user: int = Depends(check_credentials)):

    valid = reservation_id in id_with_reservations.get(certified_user, [])

    for reservation in book:
        if (reservation_id == reservation[0] and
                event_name.lower().replace(' ', '') == reservation[2].lower().replace(' ', '')):

            if not valid:
                raise HTTPException(
                    status_code=403,
                    detail="Reservation not found in user's account"
                )

            book.remove(reservation)
            cancel_book.append(reservation)

            data[reservation[2]] += reservation[3]

            return {
                'Reservation id': reservation_id,
                'Event name': reservation[2],
                'Cancelled tickets': reservation[3]
            }

    raise HTTPException(status_code=404, detail='Not found')



@app.get('/reservations/details/client/{reservation_id}')
def Reservation_info(
        reservation_id: int,
        certified_user: int = Depends(check_credentials)):

    for reservation in book:
        if reservation_id == reservation[0]:

            if reservation_id not in id_with_reservations.get(certified_user, []):
                raise HTTPException(status_code=403, detail='Access denied')

            return {
                'Status': 'active',
                'Reservation id': reservation_id,
                'Customer name': reservation[1],
                'Event_name': reservation[2],
                'Tickets': reservation[3]
            }

    for cancellation in cancel_book:
        if reservation_id == cancellation[0]:

            if reservation_id not in id_with_reservations.get(certified_user, []):
                raise HTTPException(status_code=403, detail='Access denied')

            return {
                'Status': 'cancelled',
                'Reservation id': reservation_id,
                'Customer name': cancellation[1],
                'Event_name': cancellation[2],
                'Tickets': cancellation[3]
            }

    raise HTTPException(status_code=404, detail='Not found')



@app.get('/reservations/details/{event_name}')
def Reservations_by_event(
        event_name: str,
        limit: int = 10,
        offset: int = 0,
        certified_user: int = Depends(check_credentials)):

    if limit <= 0 or offset < 0:
        raise HTTPException(status_code=400, detail='Bad request')

    for key in data.keys():
        if event_name.lower().replace(' ', '') == key.lower().replace(' ', ''):

            details = []
            user_reservations = id_with_reservations.get(certified_user, [])

            for reservation in book:
                if reservation[2] == key and reservation[0] in user_reservations:
                    details.append({
                        'Reservation id': reservation[0],
                        'Customer name': reservation[1],
                        'Event name': reservation[2],
                        'Tickets': reservation[3]
                    })

            return {
                'Event name': key,
                'Reservations': len(details),
                'Details': details[offset:offset + limit]
            }

    raise HTTPException(status_code=404, detail='Not found')




credentials = {}
User_id = 0
id_with_reservations= {}

class confidential(BaseModel):
    username : str = Field(description='length must be at least 3 characters')
    password : str = Field(description='length must be at least 8 characters')

class guest_data(BaseModel):
    username: str = Field(description='length must be at least 3 characters')
    password: str = Field(description='length must be at least 8 characters')
    reservation_number: int | None = None
    confirm_code: str | None = None



@app.post('/main_page/sign_up')
def client_credentials(user_data: guest_data):
    global credentials
    global User_id
    global id_with_reservations
    reservation_number = user_data.reservation_number
    confirm_code = user_data.confirm_code
    message = 'No guest reservations'


    if (user_data.username.strip() == '' or user_data.username.strip().isdigit()
    or user_data.username.strip() == 'string') :
        raise HTTPException(status_code=400, detail='Invalid Username')
    elif len(user_data.username.strip()) <3 :
        raise HTTPException(status_code=400, detail='Username must contain 3 or more characters')
    if user_data.password.strip() == '' or user_data.password.strip() == 'string':
        raise HTTPException(status_code=400, detail='Invalid Password')
    elif len(user_data.password.strip()) < 8 :
        raise HTTPException(status_code=400, detail='Password must contain 8 or more characters')

    hasher = PasswordHash.recommended()

    reservation_valid = False
    if reservation_number != None and confirm_code != None:
        message = 'None of the reservation details match previous reservations'
        for item in id_with_confirm_code:
            if {reservation_number:confirm_code} == item:
                reservation_valid = True
    elif (reservation_number != None and confirm_code == None or
          reservation_number == None and confirm_code != None):
         message = 'Incomplete reservation details'


    if user_data.username.strip() not in credentials.keys():
        credentials[user_data.username.strip()] = [hasher.hash(user_data.password)]
        User_id += 1
        credentials[user_data.username.strip()].append(User_id)

        if reservation_valid:
            if any(reservation_number in item for item in id_with_reservations.values()):
                message = 'The reservation is linked to another account'
            else:
                id_with_reservations[User_id] = id_with_reservations.get(User_id, []) + [reservation_number]
                message = 'Previous reservation has been added to the account'

        return {'Username': user_data.username,
                'User id': User_id,
                'Account': 'Account created successfully',
                'Message': message}
    else:
        raise HTTPException(status_code=409 ,detail = 'Username already used')





confirm_codes_login = []
@app.post('/main_page/login')
def client_login(user_data: confidential):
    hasher = PasswordHash.recommended()

    if user_data.username.strip() not in credentials.keys():
        raise HTTPException(status_code=401, detail='Invalid credentials')

    check = hasher.verify(user_data.password,credentials[user_data.username.strip()][0])
    if check == True:
        code_after_login = secrets.token_urlsafe(32)
        confirm_codes_login.append((code_after_login,credentials[user_data.username.strip()][1]))
        return {'Username': user_data.username.strip(),
                'Code after login': code_after_login,
                'Login': f'{user_data.username} successsfully logged in'}
    else:
        raise HTTPException(status_code=401, detail='Invalid credentials')



class reservation_confirm_only(BaseModel):
    reservation_number : int
    confirm_code : str

@app.post('/main_page/client')
def add_reservations(user_data : reservation_confirm_only,check=Depends(check_credentials)):
    reservation_number = user_data.reservation_number
    confirm_code = user_data.confirm_code


    for item in id_with_confirm_code:
        if {reservation_number: confirm_code} == item:
            if any(reservation_number in item for item in id_with_reservations.values()):
                raise HTTPException(status_code=409, detail='The reservation has already been added')
            id_with_reservations[check]= id_with_reservations.get(check,[]) + [reservation_number]
            return 'Reservation added to your account'
    raise HTTPException(status_code=404, detail= 'Reservation not found')







































