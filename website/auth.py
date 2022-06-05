from flask import Blueprint, render_template, request, flash, redirect, url_for, session, request, g
from .models import Administrator, Customer, Reservation, Room
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user
from datetime import datetime
from flask_qrcode import QRcode

#app = Flask(__name__)
#qrcode = QRcode(app)

auth = Blueprint('auth', __name__)

@auth.route('/welcome', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        checkIn = request.form.get('checkIn')
        checkOut = request.form.get('checkOut')
        session['rType'] = request.form.get('rType')        
        
        sevices = request.form.get('Services')
        if(sevices == "View Services" ):
            return redirect(url_for('auth.services'))  

        session['checkIn'] = checkIn
        session['checkOut'] = checkOut

        resetAvailability()
        checkAvailability()          

        if checkOut<=checkIn:
            flash("Check-Out Date must be at least one day later than Check-In Date", category='error')
            return redirect(url_for('auth.index'))
        else:
            return redirect(url_for('auth.reservation'))          
        
    return render_template("index.html", customer=current_user)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        emailAddress = request.form.get('emailAddress')
        password = request.form.get('password')

        customer = Customer.query.filter_by(emailAddress=emailAddress).first()
        if customer:
            if customer.password == password:
                flash('Logged in successfully!', category='success')
                login_user(customer, remember=True)
                return redirect(url_for('auth.customer_home'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template("login.html", customer=current_user)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        customerID = request.form.get('id') 
        emailAddress = request.form.get('emailAddress')
        firstName = request.form.get('firstName')
        lastName = request.form.get('lastName')
        password = request.form.get('password')
        phoneNumber = request.form.get('phoneNumber')
        cardNum = request.form.get('cardNum')

        customer = Customer.query.filter_by(emailAddress=emailAddress).first()
        if customer:
            flash('Email already exists.', category='error')
        elif len(emailAddress) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif "@" not in emailAddress:
            flash('Email must contain an @.', category='error')
        elif len(firstName) < 2 or len(firstName) > 15:
            flash('First name must be greater than 1 or lesser than 15 characters.', category='error')
        elif len(lastName) < 2 or len(firstName) > 15:
            flash('Last name must be greater than 1 or lesser than 15 characters.', category='error')
        elif len(password) < 7 or len(password) > 20:
            flash('Password must be at least 7 characters.', category='error')
        elif phoneNumber.strip().isdigit() == False or len(phoneNumber) > 15:
            flash('Phone Number is Invalid.', category='error')
        elif  len(cardNum) < 16 or len(cardNum) > 20:
            flash('Card Number is Invalid. Must be between 16 and 20 digits.', category='error')
        else:
            new_customer = Customer(id=customerID, emailAddress=emailAddress, firstName=firstName, lastName=lastName, password=password, phoneNumber=phoneNumber, cardNum=cardNum)
            db.session.add(new_customer)
            db.session.commit()
            login_user(new_customer, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('auth.customer_home'))

    return render_template("sign_up.html", customer=current_user)

@auth.route('/reservation', methods=['GET', 'POST'])
@login_required
def reservation():
    rType = session.get('rType')
    if rType == "All":
        rooms = Room.query.all()
    else:
        rooms = Room.query.filter_by(rType=rType).all()
    
    length = len(rooms)    

    checkIn = session.get('checkIn')
    checkOut = session.get('checkOut')    
    if(checkIn == None or checkOut == None):
        checkIn = "2021-01-01"
        checkOut = "2021-01-08"

    if request.method == 'POST':
        checkIn = session.get('checkIn')
        checkOut = session.get('checkOut') 
        id = request.form.get('id')
        cardNum = request.form.get('cardNum')
        password = request.form.get('password')
        x = datetime.strptime(checkIn, '%Y-%m-%d')
        y = datetime.strptime(checkOut, '%Y-%m-%d')
        user_id = current_user.get_id()        
        roomNum = request.form.get("action")         
        customer = Customer.query.filter_by(id=user_id).first()

        if customer:            
            if customer.password == password and customer.cardNum == cardNum:
                room = Room.query.filter_by(roomNum=roomNum).first()
                new_reservation = Reservation(id=id, totalCost=room.costPerNight, checkIn=x, checkOut=y, customer_id=user_id, roomNum=room.roomNum)
                db.session.add(new_reservation)
                db.session.commit()
                flash('Reservation Booked!', category='success')
                return redirect(url_for('auth.customer_home'))
            else:
                flash('Incorrect User Details!', category='error')

    return render_template("reservation.html", customer=current_user, checkIn=checkIn, checkOut=checkOut, length=length, rooms=rooms)

def checkAvailability():
    reservations = Reservation.query.all()
    rooms = Room.query.all()
    checkIn = session.get('checkIn')

    if(checkIn == None):
        checkIn = "2021-01-01"

    checkIndate = datetime.strptime(checkIn, '%Y-%m-%d')
    for reservation in reservations:
        for room in rooms:
            roomNum = room.roomNum
            if (checkIndate.date() <= reservation.checkOut and roomNum == reservation.roomNum):
                room = Room.query.filter_by(roomNum=roomNum).first()
                room.available = False
                db.session.commit()

def resetAvailability():
    reservations = Reservation.query.all()
    rooms = Room.query.all()
    for room in rooms:
        roomNum = room.roomNum
        room = Room.query.filter_by(roomNum=roomNum).first()        
        room.available = True
        db.session.commit()
    
@auth.route('/admin_portal', methods=['GET', 'POST'])
def admin_portal():
    if request.method == 'POST':
        customerID = request.form.get('customerID') 
        emailAddress = request.form.get('emailAddress')
        cardNum = request.form.get('cardNum')
        password = request.form.get('password')
        phoneNumber = request.form.get('phoneNumber')
        firstName = request.form.get('firstName')
        lastName = request.form.get('lastName')

        customer = Customer.query.filter_by(customerID=customerID).first()
        if customer:
            flash('User already exists', category='error')
        if len(emailAddress) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(firstName) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif len(password) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            new_customer = Customer(customerID=customerID, emailAddress=emailAddress, cardNum=cardNum, firstName=firstName, lastName=lastName, password=password, phoneNumber=phoneNumber)
            db.session.add(new_customer)
            db.session.commit()
            flash('Account created!', category='success')    
    return render_template("admin_portal.html", customer=current_user)

def calculateDateLength():    
    checkIn = session.get('checkIn')
    checkOut = session.get('checkOut') 

    if(checkIn == None or checkOut == None):
        checkIn = "2021-01-01"
        checkOut = "2021-01-08"    
    checkIndate = datetime.strptime(checkIn, '%Y-%m-%d')
    checkOutdate = datetime.strptime(checkOut, '%Y-%m-%d')
    delta = checkOutdate - checkIndate
    return(delta.days)

def calculateBill():
    services = 0      
    amountOfNights = calculateDateLength()
    user_id = current_user.get_id()
    res_data = Reservation.query.filter_by(customer_id=user_id).first()    

    if(res_data == None):
        nightlyCost = 0
    else:
        nightlyCost = res_data.totalCost
    totalCost = (nightlyCost * amountOfNights) + services
    return totalCost

def inputdata(self):
    self.id=input("\nEnter your Customer ID:")
    self.firstName=input("\nEnter your First Name:")
    self.lastName=input("\nEnter your Last Name:")
    self.emailAddress=input("\nEnter your address:")
    self.checkIn=input("\nEnter your check in date:")
    self.checkOut=input("\nEnter your checkout date:")
    print("Your room no.:",self.roomNum,"\n")

@auth.route('/admin_login', methods=['GET'])
def admin_login():
     if request.method == 'POST':
         adminID = request.form.get('admin.id')
         password = request.form.get('admin.password')

     admin = Admin.query.filter_by(id=adminID).first()
     if admin:
             if check_password_hash(admin.password, password):
                 flash('Logged in successfully!', category='success')
                 login_user(admin, remember=True)
                
             else:
                 flash('You have entered a wrong password, please try again.', category='error')
     else:
         flash('You have entered the wrong ID, please try again.', category='error')

     return render_template("admin_login.html", admin=current_user)

@auth.route('/', methods=['GET', 'POST'])
def customer_home(): 
    user_id = current_user.get_id()
    reservation = Reservation.query.filter_by(customer_id=user_id).first()
    #STRING_TO_ENCODE = str(user_id)     
    
    if(reservation == None): 
        checkIn = "N/A"
        checkOut = "N/A"
        room = "N/A"     
        nights = 0
        roomCost = 0 
    else:       
        checkIn = reservation.checkIn
        checkOut = reservation.checkOut 
        room = reservation.roomNum 
        roomCost = reservation.totalCost 

        nights = checkOut - checkIn

    if request.method == 'POST':
        finalCheckOut = request.form.get("Check Out of Hotel")
        cancel = request.form.get("Cancel Reservation")
        delete = request.form.get("Delete Account")
        
        if cancel == "Cancel Reservation":
            if(reservation == None): 
                flash("No reservation to cancel!", category='error')
            else:
                return redirect(url_for('auth.cancel_reservation'))

        if delete == "Delete Account": 
            user_id = current_user.get_id()
            customer = Customer.query.filter_by(id=user_id).first() 
            db.session.delete(customer)
            db.session.commit()
            flash("Account has been deleted.", category='success')
            return redirect(url_for('auth.index'))

        if finalCheckOut == "Check Out of Hotel":
            if(reservation == None): 
                flash("No reservation to check out!", category='error') 
                return render_template('customer_home.html', customer=current_user, checkIn = checkIn, checkOut = checkOut, nights=nights, roomCost=roomCost, bill = calculateBill())
            else:
                db.session.delete(reservation)
                db.session.commit()
                flash("Customer has checked out! Reservation deleted", category='success')
  
    return render_template('customer_home.html', customer=current_user, room=room, checkIn = checkIn, checkOut = checkOut, nights=nights, roomCost=roomCost, bill = calculateBill())

@auth.route('/cancel_reservation', methods=['GET', 'POST'])
def cancel_reservation():
    user_id = current_user.get_id()
    reservation = Reservation.query.filter_by(customer_id=user_id).first()
    if(reservation == None): 
        checkIn = "N/A"
        checkOut = "N/A"  
        room = "N/A"     
    else:       
        checkIn = reservation.checkIn
        checkOut = reservation.checkOut
        room = reservation.roomNum 

    if request.method == 'POST':       
        deleteReservation = request.form.get("Delete reservation") 
        db.session.delete(reservation)
        db.session.commit()
        flash("Reservation has been deleted", category='success')
        return redirect(url_for('auth.customer_home'))        
    
    return render_template('cancel_reservation.html', customer=current_user, room=room, checkIn = checkIn, checkOut = checkOut)

@auth.route('/services', methods=['GET', 'POST'])
def services():
    return render_template('services.html', customer=current_user)

#@auth.route('/qrcode', methods=["GET"])
#def get_qrcode():
    # please get /qrcode?data=<qrcode_data>
    #data = request.args.get("data", "")
    #return send_file(qrcode(data, mode="raw"), mimetype="image/png")


