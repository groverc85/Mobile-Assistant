from moblife import db


class ActTour(db.Model):
    __bind_key__ = 'xms'
    __tablename__ = "ActTour"
    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.Integer)
    title = db.Column(db.String(20))
    note = db.Column(db.String(50))
    start_city = db.Column(db.String(16))
    start_address = db.Column(db.String(80))
    dest_city = db.Column(db.String(16))
    dest_address = db.Column(db.String(80))
    begin_datetime = db.Column(db.DateTime)
    end_datetime = db.Column(db.DateTime)
    ordered = db.Column(db.Boolean)

    def __init__(self, userid, title, note, start_city, start_address, dest_city, dest_address, begin_datetime, end_datetime, ordered):
        #self.id = id
        self.userid = userid
        self.title = title
        self.note = note
        self.start_city = start_city
        self.start_address = start_address
        self.dest_city = dest_city
        self.dest_address = dest_address
        self.begin_datetime = begin_datetime
        self.end_datetime = end_datetime
        self.ordered = ordered
    #def __repr__(self):
    #    return '<User %r>' % (self.name)


class ActPref(db.Model):
    #docstring for ActPref
    __bind_key__ = 'xms'
    __tablename__ = "ActPref"
    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.Integer)
    # leaving trip, start for start, dest for destination
    leave_main_traffic = db.Column(db.String(10))
    leave_start_traffic = db.Column(db.String(10))
    leave_dest_traffic = db.Column(db.String(10))
    # returning trip, reverse to that of leaving
    return_main_traffic = db.Column(db.String(10))
    return_start_traffic = db.Column(db.String(10))
    return_dest_traffic = db.Column(db.String(10))

    wait_bus_buffer = db.Column(db.Integer)
    wait_taxi_buffer = db.Column(db.Integer)
    # for train
    train_qos = db.Column(db.String(20))
    train_type = db.Column(db.String(20))
    wait_train_buffer = db.Column(db.Integer)
    # for flight
    flight_qos = db.Column(db.String(20))
    flight_company = db.Column(db.String(100))
    wait_flight_buffer = db.Column(db.Integer)
    # for hotel
    hotel = db.Column(db.String(100))
    hotel_radius = db.Column(db.Integer)
    check_in_buffer = db.Column(db.Integer)
    check_out_buffer = db.Column(db.Integer)
    # for restaurant
    restaurant = db.Column(db.String(100))
    restaurant_radius = db.Column(db.Integer)
    meal_buffer = db.Column(db.Integer)
    # for activity
    wait_act_buffer = db.Column(db.Integer)

    def __init__(self, userid, leave_main_traffic, leave_start_traffic, leave_dest_traffic, 
                 return_main_traffic, return_start_traffic, return_dest_traffic,
                 wait_bus_buffer, wait_taxi_buffer, train_qos, train_type, wait_train_buffer,
                 flight_qos, flight_company, wait_flight_buffer, hotel, hotel_radius,
                 check_in_buffer, check_out_buffer, restaurant, restaurant_radius,
                 meal_buffer, wait_act_buffer):
        #super(Act_qos, self).__init__()
        self.userid = userid
        # leave
        self.leave_main_traffic = leave_main_traffic
        self.leave_start_traffic = leave_start_traffic
        self.leave_dest_traffic = leave_dest_traffic
        # return
        self.return_main_traffic = return_main_traffic
        self.return_start_traffic = return_start_traffic
        self.return_dest_traffic = return_dest_traffic
        
        self.wait_bus_buffer = wait_bus_buffer
        self.wait_taxi_buffer = wait_taxi_buffer
        # for train
        self.train_qos = train_qos
        self.train_type = train_type
        self.wait_train_buffer = wait_train_buffer
        # for flight
        self.flight_qos = flight_qos
        self.flight_company = flight_company
        self.wait_flight_buffer = wait_flight_buffer
        # hotel
        self.hotel = hotel
        self.hotel_radius = hotel_radius
        self.check_in_buffer = check_in_buffer
        self.check_out_buffer = check_out_buffer
        # restaurant
        self.restaurant = restaurant
        self.restaurant_radius = restaurant_radius
        self.meal_buffer = meal_buffer
        self.wait_act_buffer = wait_act_buffer


class Timeline(db.Model):
    #docstring for ActPref
    __bind_key__ = 'xms'
    __tablename__ = "Timeline"
    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.Integer)
    actid = db.Column(db.Integer)
    leave_return = db.Column(db.Boolean)
    timeline = db.Column(db.Text)
    main_traffics = db.Column(db.Text)
    hotels = db.Column(db.Text)
    restaurants = db.Column(db.Text)

    def __init__(self, userid, actid, leave_return, timeline, main_traffics, hotels, restaurants):
        #super(Act_pref, self).__init__()
        self.userid = userid
        self.actid = actid
        self.leave_return = leave_return
        self.timeline = timeline
        self.main_traffics = main_traffics
        self.hotels = hotels
        self.restaurants = restaurants


'''
class MainTraffic(db.Model):
    #docstring for ActPref
    __bind_key__ = 'xms'
    __tablename__ = "MainTraffic"
    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.Integer)
    actid = db.Column(db.Integer)
    timelineid = db.Column(db.Integer)
    leave_return = db.Column(db.Boolean)
    traffics = db.Column(db.Text)

    def __init__(self, userid, actid, timeline, leave_return, traffics):
        #super(Act_pref, self).__init__()
        self.userid = userid
        self.actid = actid
        self.timelineid = timelineid
        self.leave_return = leave_return
        self.traffics = traffics


class Hotel(db.Model):
    #docstring for ActPref
    __bind_key__ = 'xms'
    __tablename__ = "Hotel"
    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.Integer)
    actid = db.Column(db.Integer)
    timelineid = db.Column(db.Integer)

    def __init__(self, userid, actid, timeline):
        #super(Act_pref, self).__init__()
        self.userid = userid
        self.actid = actid
        self.timelineid = timelineid


class Restaurant(db.Model):
    #docstring for ActPref
    __bind_key__ = 'xms'
    __tablename__ = "Restaurant"
    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.Integer)
    actid = db.Column(db.Integer)
    timelineid = db.Column(db.Integer)

    def __init__(self, userid, actid, timeline):
        #super(Act_pref, self).__init__()
        self.userid = userid
        self.actid = actid
        self.timelineid = timelineid
'''