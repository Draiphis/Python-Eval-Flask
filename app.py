from flask import Flask, jsonify, request,render_template,flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
import locale
from pydantic import BaseModel, ValidationError, Field
from sqlalchemy import select

app = Flask(__name__)
app.secret_key = "j'adore_flask"

locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///event_db.db'


db = SQLAlchemy(app)

# 🔹 Modèle HistoryEntry
class Event(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    event_type = db.Column(db.String(50), nullable=False)
    event_proposed_date = db.Column(db.Date, nullable=False)
    event_place = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(50000), nullable=False)
    proposition_creation_date = db.Column(db.Date, default=datetime.now(timezone.utc),  nullable=False)

    
    

    def __repr__(self):
        return f"Room ('{self.title}','{self.event_type}','{self.event_proposed_date}','{self.event_place}','{self.description}','{self.proposition_creation_date}')"
    
class PrintEventRequest(BaseModel):
    title : str = Field(min_length=1, max_length=80)
    event_type : str = Field(min_length=1, max_length=80)
    event_proposed_date : datetime = Field(ge=datetime.now())
    event_place : str = Field(min_length=1, max_length=100)
    description : str = Field(min_length=1, max_length=500)
    



with app.app_context():
    db.create_all()




@app.route("/", methods=['GET'])
def home():
    entries=Event.query.all()
    return render_template("index.html", entries=entries)


@app.route("/create-event", methods=['GET', 'POST'])
def form():

    if request.method == "POST":
        has_error = False
           
        
        title = str(request.form.get("titre", "").strip())
        if not title: 
            has_error = True
            flash("Veuillez saisir un titre", "error")
        
        event_type = request.form.get("type", "").strip()
        if not event_type: 
            has_error = True
            flash("Veuillez selectionner un type d'événement", "error")
        
        event_date_raw = request.form.get("event_date", "").strip()
        try:
            event_proposed_date = datetime.strptime(event_date_raw, "%Y-%m-%d")
            if event_proposed_date < datetime.now():
                raise ValueError
        except ValueError:
            has_error = True
            flash(
                "Nous n'avons pas encore de machine à remonter dans le temps. "
                "Veuillez saisir une date après aujourd'hui",
                "error"
            )
        
        event_place = request.form.get("lieu", "").strip()
        if not event_place: 
            has_error = True
            flash("Veuillez indiquer le lieu de l'événement", "error")
        
        description = request.form.get("desc", "").strip()
        if not description: 
            has_error = True
            flash("Veuillez décrire votre événement", "error")

        if not has_error:
            
            entry = Event(title=title, event_type=event_type, event_proposed_date=event_proposed_date, event_place=event_place, description=description)
            db.session.add(entry)
            db.session.commit()
    return render_template("form.html")



# @app.route("/print-event", methods=['GET'])
# def print_events():
#     events=Event.query.all()
#     clean_events=[]
#     for e in events:
#         clean_events.append({
#             "id":e.id,
#             "title":e.title,
#             "event_type":e.event_type,
#             "event_proposed_date":e.event_proposed_date,
#             "event_place":e.event_place,
#             "description":e.description,
#             "proposition_creation_date":e.proposition_creation_date
#         })
#     return jsonify({
#         "events": clean_events
#     })
# @app.route("/print-event", methods=["POST"])
# def print_event():

#     data = request.get_json(silent=True)
#     if not data :
#         return jsonify({"error":"INVALID_JSON", "message":"Invalid JSON"}),400
    
#     try:
#         validated_data = PrintEventRequest.model_validate(data)
#     except ValidationError as e:
#         return jsonify({"error" : "VALIDATION_ERROR", "message":e.errors()}), 400
    
#     event =db.session.execute(
#         select(Event.id).where(Event.title==validated_data.title)
#     ).one_or_none()
#     if event is not None:
#         return jsonify({"error" : "EVENT_ALREADY_EXISTS", "message":"Event with this title already exists"}), 409


#     new_event = Event()
#     new_event.title=validated_data.title
#     new_event.event_type=validated_data.event_type
#     new_event.event_proposed_date=validated_data.event_proposed_date
#     new_event.event_place=validated_data.event_place
#     new_event.description=validated_data.description
#     new_event.proposition_creation_date=datetime.now(timezone.utc)

#     db.session.add(new_event)
#     db.session.commit()

#     return  jsonify({
#         "id": new_event.id,
#         "title": new_event.title,
#         "event_type": new_event.event_type,
#         "event_proposed_date": new_event.event_proposed_date,
#         "event_place": new_event.event_place,
#         "description": new_event.description,
#         "proposition_creation_date": new_event.proposition_creation_date
#     }),201
