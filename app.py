from flask import *
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3, os, uuid

app = Flask(__name__)
app.secret_key = "GREENMOTION_CHANGE_THIS_SECRET"

DB = "greenmotion.db"
UPLOAD = "static/uploads"
os.makedirs(UPLOAD, exist_ok=True)

ADMIN_USER = "admin"
ADMIN_PASS = "Green@12345"

def db():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    return con

def init_db():
    con = db()
    con.execute("""
    CREATE TABLE IF NOT EXISTS cars(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        brand TEXT,
        year TEXT,
        price TEXT,
        condition TEXT,
        transmission TEXT,
        description TEXT,
        whatsapp TEXT,
        image TEXT
    )
    """)
    con.commit()

    if con.execute("SELECT COUNT(*) FROM cars").fetchone()[0] == 0:
        samples = [
            ("Mercedes-Benz GLE 350","Mercedes","2022","₦48,500,000","Foreign Used","Automatic","Luxury SUV","2348012345678","https://images.unsplash.com/photo-1618843479313-40f8afb4b4d8?w=900"),
            ("Toyota Land Cruiser","Toyota","2021","₦75,000,000","Foreign Used","Automatic","Premium SUV","2348012345678","https://images.unsplash.com/photo-1519641471654-76ce0107ad1b?w=900"),
            ("Lexus RX 350","Lexus","2020","₦32,000,000","Tokunbo","Automatic","Luxury crossover","2348012345678","https://images.unsplash.com/photo-1606664515524-ed2f786a0bd6?w=900")
        ]
        con.executemany("""
        INSERT INTO cars(name,brand,year,price,condition,
        transmission,description,whatsapp,image)
        VALUES(?,?,?,?,?,?,?,?,?)
        """, samples)
        con.commit()
    con.close()

STYLE = """
<style>
*{box-sizing:border-box}
body{margin:0;background:#050a07;color:white;font-family:Arial}
header{background:#09150d;padding:20px 6%;display:flex;
justify-content:space-between;align-items:center;border-bottom:1px solid #1b6035}
.logo{font-size:23px;font-weight:bold;color:#39ff85;text-shadow:0 0 12px #39ff85}
a{color:#39ff85;text-decoration:none}
button,.btn{background:#32f477;color:#001b09;border:0;padding:13px 19px;
border-radius:7px;font-weight:bold;cursor:pointer;text-decoration:none}
input,select,textarea{width:100%;padding:14px;margin:9px 0;
background:#101d14;border:1px solid #27613a;color:white;border-radius:7px}
.container{max-width:1100px;margin:35px auto;padding:15px}
.box{background:#0d1911;padding:24px;border:1px solid #205632;
border-radius:12px;margin-bottom:20px}
h1,h2{color:#39ff85}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:20px}
.card{background:#0c1810;border:1px solid #245334;border-radius:12px;overflow:hidden}
.card img{width:100%;height:190px;object-fit:cover}
.content{padding:17px}
.price{color:#39ff85;font-size:23px;font-weight:bold;margin:15px 0}
.small{color:#a6b6aa;line-height:1.8}
.hero{padding:90px 8%;background:linear-gradient(90deg,#020a05,#001507aa),url('https://images.unsplash.com/photo-1492144534655-ae79c964c9d7?w=1500') center/cover}
.hero h1{font-size:48px;color:white}
.hero span{color:#39ff85}
footer{text-align:center;padding:30px;color:#809487}
@media(max-width:600px){.hero h1{font-size:35px}header{padding:16px}.logo{font-size:18px}}
</style>
"""


@app.route("/")
def home():
    con = db()
    search = request.args.get("search", "").lower()
    brand = request.args.get("brand", "")
    all_cars = con.execute("SELECT * FROM cars ORDER BY id DESC").fetchall()
    con.close()

    cars = [
        c for c in all_cars
        if search in (c["name"] + " " + c["brand"]).lower()
        and (not brand or c["brand"] == brand)
    ]
    brands = sorted(set(c["brand"] for c in all_cars))

    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
    <title>GREENMOTION AUTOS | Luxury Car Marketplace</title>
    <meta name="viewport" content="width=device-width,initial-scale=1">
    """+STYLE+"""
    <style>
    html{scroll-behavior:smooth}
    .hero{min-height:560px;display:flex;align-items:center}
    .hero h1{font-size:55px;line-height:1.15}
    .hero p{font-size:17px;line-height:1.9;max-width:600px}
    .tagline{color:#39ff85;letter-spacing:4px;font-weight:bold;font-size:12px}
    .green{color:#39ff85}
    .stats{display:grid;grid-template-columns:repeat(3,1fr);gap:15px}
    .stat,.feature,.review{background:#0d1911;border:1px solid #245b38;border-radius:12px;padding:25px}
    .stat{text-align:center}
    .stat h2{font-size:27px}
    .stat p,.feature p,.review p{color:#aabbb0;line-height:1.8}
    .feature h3,.review h3{color:#39ff85;margin-bottom:12px}
    .section-heading{margin-bottom:30px}
    .section-heading h2{font-size:32px}
    .grid{margin-top:25px}
    .card img{transition:.4s}
    .card:hover img{transform:scale(1.04)}
    .card:hover{box-shadow:0 0 25px #39ff8540}
    .card .btn{display:block;text-align:center}
    .price{font-size:24px}
    .offer{padding:50px 25px;text-align:center;border:1px solid #39ff85;
    border-radius:15px;background:linear-gradient(120deg,#10351d,#061009)}
    .offer h2{font-size:35px}
    .offer p{color:#bdcfc1;line-height:1.9;margin:20px auto;max-width:650px}
    .contact-box{text-align:center;padding:55px 20px;border:1px solid #39ff85;
    border-radius:15px;background:linear-gradient(120deg,#10351d,#061009)}
    @media(max-width:600px){
    .hero{min-height:460px;padding:60px 6%}
    .hero h1{font-size:38px}
    .stats{grid-template-columns:1fr}
    .section-heading h2{font-size:25px}
    .offer h2{font-size:27px}
    header nav a{font-size:11px;margin-left:5px}
    }
    </style>
    
<style>
/* GREENMOTION PREMIUM NEON REDESIGN */

:root {
 --green:#39ff85;
 --dark:#030805;
 --panel:#09140d;
 --border:#174b2b;
}

html {
 scroll-behavior:smooth;
}

body {
 background:
 radial-gradient(ellipse at 10% 5%,#10351b 0%,transparent 35%),
 radial-gradient(ellipse at 90% 35%,#092518 0%,transparent 35%),
 #030805 !important;
 color:#f5fff7 !important;
}

header {
 background:rgba(3,12,7,.94) !important;
 backdrop-filter:blur(18px);
 border-bottom:1px solid #39ff8555 !important;
 box-shadow:0 5px 30px #00ff331c;
 position:sticky;
 top:0;
 z-index:100;
}

.logo {
 color:#39ff85 !important;
 text-shadow:0 0 8px #39ff85,0 0 25px #00ff66 !important;
 letter-spacing:2px;
}

nav a {
 transition:.3s;
}

nav a:hover {
 color:#39ff85 !important;
 text-shadow:0 0 12px #39ff85;
}

.hero {
 min-height:590px !important;
 position:relative;
 overflow:hidden;
 background:
 linear-gradient(90deg,rgba(0,8,3,.96),rgba(0,15,7,.58),rgba(0,0,0,.15)),
 url('https://images.unsplash.com/photo-1492144534655-ae79c964c9d7?w=1800') center/cover !important;
 border-bottom:1px solid #39ff8544;
}

.hero:after {
 content:"";
 position:absolute;
 bottom:0;
 left:0;
 width:100%;
 height:3px;
 background:#39ff85;
 box-shadow:0 0 15px #39ff85,0 0 35px #39ff85;
}

.hero h1 {
 text-shadow:0 0 25px #000;
 letter-spacing:-2px;
}

.hero h1 span,
.green {
 color:#39ff85 !important;
 text-shadow:0 0 15px #39ff8577;
}

.tagline {
 text-shadow:0 0 12px #39ff85;
}

.btn,button {
 background:linear-gradient(135deg,#39ff85,#00c853) !important;
 color:#001b09 !important;
 border:1px solid #83ffb2 !important;
 border-radius:8px !important;
 box-shadow:0 0 12px #39ff8555,0 0 30px #39ff8522 !important;
 transition:all .3s ease !important;
 font-weight:900 !important;
}

.btn:hover,button:hover {
 transform:translateY(-4px);
 box-shadow:0 0 15px #39ff85,0 0 40px #39ff8577 !important;
}

.container {
 position:relative;
}

.stat,.feature,.review,.testimonial {
 background:linear-gradient(145deg,#102319,#07110b) !important;
 border:1px solid #39ff8544 !important;
 box-shadow:0 0 20px #00ff6610,inset 0 0 20px #39ff8508;
 transition:.3s;
}

.stat:hover,.feature:hover,.review:hover,.testimonial:hover {
 border-color:#39ff85 !important;
 box-shadow:0 0 25px #39ff8533;
 transform:translateY(-5px);
}

.card {
 background:linear-gradient(145deg,#102018,#07100a) !important;
 border:1px solid #39ff8544 !important;
 border-radius:15px !important;
 overflow:hidden;
 box-shadow:0 5px 25px #0008;
 transition:.35s;
}

.card:hover {
 transform:translateY(-8px);
 border-color:#39ff85 !important;
 box-shadow:0 0 15px #39ff8555,0 0 35px #00ff6622 !important;
}

.card img {
 width:100%;
 height:220px !important;
 object-fit:cover;
 transition:.5s;
}

.card:hover img {
 transform:scale(1.06);
}

.content {
 padding:22px !important;
}

.card h2 {
 color:#fff !important;
}

.price {
 color:#39ff85 !important;
 text-shadow:0 0 12px #39ff8566;
 font-weight:900;
}

.badge {
 background:#0d4224 !important;
 color:#39ff85 !important;
 border:1px solid #39ff8566;
 box-shadow:0 0 12px #39ff8522;
}

input,select,textarea {
 background:#07130b !important;
 border:1px solid #39ff8544 !important;
 color:white !important;
 border-radius:9px !important;
}

input:focus,select:focus,textarea:focus {
 outline:none;
 border-color:#39ff85 !important;
 box-shadow:0 0 15px #39ff8544;
}

.offer,.contact-box {
 background:
 radial-gradient(circle at top right,#164d2a,#07130b 65%) !important;
 border:1px solid #39ff85 !important;
 box-shadow:0 0 25px #39ff8522, inset 0 0 30px #39ff8510;
 border-radius:20px !important;
}

.section-heading {
 border-left:3px solid #39ff85;
 padding-left:18px;
}

footer {
 background:#020603 !important;
 border-top:1px solid #39ff8555;
 box-shadow:0 -5px 30px #00ff3311;
 padding:35px 15px !important;
}

footer a {
 color:#39ff85 !important;
}

.small {
 color:#b5c8ba !important;
 line-height:1.9;
}

#cars,#why,#contact {
 scroll-margin-top:100px;
}

/* Better arrangement */
.hero {order:1}
.stats {order:2}
#cars {order:3}
#why {order:4}
#contact {order:6}

@media(max-width:650px) {
 .hero {
  min-height:480px !important;
  padding:65px 6% !important;
  background-position:60% center !important;
 }
 .hero h1 {
  font-size:39px !important;
 }
 .card img {
  height:200px !important;
 }
 .section-heading h2 {
  font-size:25px !important;
 }
 .btn {
  font-size:12px;
 }
 header {
  padding:15px 4% !important;
 }
}
</style>

</head>
    <body>

    <header>
    <div class="logo">GREENMOTION.</div>
    <nav>
    <a href="/">HOME</a>
    <a href="#cars">CARS</a>
    <a href="#why">WHY US</a>
    <a href="#contact">CONTACT</a>
    </nav>
    </header>

    <section class="hero">
    <div>
    <div class="tagline">WELCOME TO GREENMOTION AUTOS</div>
    <h1>YOUR DREAM CAR.<br>YOUR <span class="green">NEXT CHAPTER.</span></h1>
    <p>
    Discover a world of exceptional automobiles.
    From breathtaking luxury sedans to powerful SUVs,
    find the perfect vehicle that matches your taste,
    ambition and lifestyle.
    </p>
    <a class="btn" href="#cars">EXPLORE OUR SHOWROOM →</a>
    </div>
    </section>

    <section class="container stats">
    <div class="stat"><h2>{{total}}+</h2><p>VEHICLES LISTED</p></div>
    <div class="stat"><h2>PREMIUM</h2><p>CAR COLLECTION</p></div>
    <div class="stat"><h2>DIRECT</h2><p>WHATSAPP ENQUIRIES</p></div>
    </section>

    <section class="container" id="cars">
    <div class="section-heading">
    <div class="tagline">DISCOVER SOMETHING EXTRAORDINARY</div>
    <h2>FIND YOUR <span class="green">PERFECT RIDE.</span></h2>
    <p class="small">Explore our collection and choose the car that moves you.</p>
    </div>

    <form method="GET">
    <input name="search" value="{{search}}" placeholder="Search Toyota, Mercedes, BMW, Lexus...">
    <select name="brand">
    <option value="">ALL BRANDS</option>
    {% for b in brands %}
    <option value="{{b}}" {% if selected == b %}selected{% endif %}>{{b}}</option>
    {% endfor %}
    </select>
    <button>SEARCH CARS →</button>
    </form>

    <div class="grid">
    {% for c in cars %}
    <div class="card">
    <img src="{{c.image}}" alt="{{c.name}}">
    <div class="content">
    <span class="badge">{{c.condition}}</span>
    <h2 style="font-size:20px;margin-top:13px">{{c.name}}</h2>
    <p class="small">
    MODEL: {{c.year}}<br>
    BRAND: {{c.brand}}<br>
    TRANSMISSION: {{c.transmission}}
    </p>
    <div class="price">{{c.price}}</div>
    <p class="small">{{c.description}}</p>
    <a class="btn" target="_blank"
    href="https://wa.me/{{c.whatsapp}}?text={{('Hello Greenmotion Autos! I am interested in buying the '+c.name+'. Please provide more details about payment and delivery.')|urlencode}}">
    BUY THIS CAR ON WHATSAPP →
    </a>
    </div></div>
    {% else %}
    <p>No matching cars found. Try another search.</p>
    {% endfor %}
    </div>
    </section>

    <section class="container">
    <div class="offer">
    <div class="tagline">THE ROAD TO YOUR DREAMS STARTS HERE</div>
    <h2>DON'T JUST DREAM IT.<br><span class="green">DRIVE IT.</span></h2>
    <p>
    Every journey deserves an extraordinary beginning.
    Find a vehicle that reflects your personality,
    complements your lifestyle and makes every drive memorable.
    Your dream car could be waiting in our showroom.
    </p>
    <a href="#cars" class="btn">EXPLORE AVAILABLE CARS</a>
    </div>
    </section>

    <section class="container" id="why">
    <div class="section-heading">
    <div class="tagline">THE GREENMOTION EXPERIENCE</div>
    <h2>WHY SHOP <span class="green">WITH US?</span></h2>
    </div>
    <div class="grid">
    <div class="feature">
    <h3>🚘 AMAZING COLLECTION</h3>
    <p>Explore different vehicle brands, models and styles in one convenient showroom.</p>
    </div>
    <div class="feature">
    <h3>💬 EASY WHATSAPP CONTACT</h3>
    <p>Ask questions and get more information directly from the seller.</p>
    </div>
    <div class="feature">
    <h3>🤝 PERSONAL SERVICE</h3>
    <p>Discuss vehicle availability, payment arrangements and delivery options.</p>
    </div>
    <div class="feature">
    <h3>✨ YOUR CHOICE MATTERS</h3>
    <p>Compare your options and take your time choosing your next vehicle.</p>
    </div>
    </div>
    </section>

    <section class="container">
    <div class="section-heading">
    <div class="tagline">MORE THAN JUST A CAR</div>
    <h2>START YOUR NEXT <span class="green">ADVENTURE.</span></h2>
    </div>
    <div class="grid">
    <div class="review">
    <h3>YOUR DREAM. YOUR DRIVE.</h3>
    <p>Find a vehicle that makes you excited to get behind the wheel every morning.</p>
    </div>
    <div class="review">
    <h3>CONFIDENCE IN EVERY CHOICE.</h3>
    <p>Contact our sales team to ask questions and discuss your preferred vehicle before purchasing.</p>
    </div>
    </div>
    </section>

    <section class="container" id="contact">
    <div class="contact-box">
    <div class="tagline">YOUR NEXT RIDE IS CALLING</div>
    <h1 style="font-size:35px;margin:18px 0">
    READY TO <span class="green">MAKE IT YOURS?</span>
    </h1>
    <p class="small" style="margin-bottom:25px">
    Have questions? Want to discuss payment or delivery?
    Send us a WhatsApp message today.
    </p>
    <a class="btn" target="_blank"
    href="https://wa.me/2348012345678?text=Hello%20Greenmotion%20Autos!%20I%20want%20to%20enquire%20about%20your%20cars.">
    CHAT WITH OUR SALES TEAM →
    </a>
    </div>
    </section>

    <footer>
    <div class="logo">GREENMOTION AUTOS</div>
    <p style="margin-top:12px">DRIVE YOUR DREAM. EXPERIENCE THE DIFFERENCE.</p>
    <p style="margin-top:15px">© 2026 GREENMOTION AUTOS. ALL RIGHTS RESERVED.</p>
    <a href="#cars">EXPLORE CARS</a>
    </footer>
    </body></html>
    """,cars=cars,brands=brands,search=request.args.get("search",""),
    selected=brand,total=len(all_cars))
@app.route("/admin", methods=["GET","POST"])
def admin_login():
    if session.get("admin"):
        return redirect("/dashboard")

    error = ""
    if request.method == "POST":
        username = request.form.get("username","")
        password = request.form.get("password","")

        if username == ADMIN_USER and password == ADMIN_PASS:
            session["admin"] = True
            return redirect("/dashboard")
        error = "Incorrect username or password"

    return render_template_string("""
    <!DOCTYPE html><html><head><title>Admin Login</title>
    <meta name="viewport" content="width=device-width,initial-scale=1">
    """+STYLE+"""</head><body>
    <div class="container"><div class="box">
    <h1>GREENMOTION ADMIN</h1>
    <p>Login to manage your car showroom.</p>
    <form method="POST">
    <input name="username" placeholder="Admin username" required>
    <input name="password" type="password" placeholder="Password" required>
    <button>LOGIN</button>
    </form>
    <p style="color:#ff7777">{{error}}</p>
    <a href="/">← Back to website</a>
    </div></div></body></html>
    """,error=error)

@app.route("/dashboard",methods=["GET","POST"])
def dashboard():
    if not session.get("admin"):
        return redirect("/admin")

    if request.method == "POST":
        name = request.form.get("name","").strip()
        brand = request.form.get("brand","").strip()
        year = request.form.get("year","").strip()
        price = request.form.get("price","").strip()
        condition = request.form.get("condition","")
        transmission = request.form.get("transmission","")
        description = request.form.get("description","").strip()
        whatsapp = request.form.get("whatsapp","").replace("+","").replace(" ","").replace("-","")

        file = request.files.get("image")
        if not all([name,brand,year,price,whatsapp,file,file.filename]):
            return "Please complete all required fields and select a car image.",400

        if not whatsapp.isdigit() or len(whatsapp) < 10:
            return "Enter a valid WhatsApp number with country code.",400

        if not file.filename.lower().endswith((".jpg",".jpeg",".png",".webp")):
            return "Image must be JPG, JPEG, PNG or WEBP.",400

        filename = str(uuid.uuid4()) + "_" + secure_filename(file.filename)
        file.save(os.path.join(UPLOAD,filename))
        image = "/static/uploads/" + filename

        con = db()
        con.execute("""
        INSERT INTO cars(name,brand,year,price,condition,
        transmission,description,whatsapp,image)
        VALUES(?,?,?,?,?,?,?,?,?)
        """,(name,brand,year,price,condition,transmission,
             description,whatsapp,image))
        con.commit()
        con.close()
        return redirect("/dashboard?success=1")

    con = db()
    cars = con.execute("SELECT * FROM cars ORDER BY id DESC").fetchall()
    total = len(cars)
    con.close()

    return render_template_string("""
    <!DOCTYPE html><html><head><title>Admin Dashboard</title>
    <meta name="viewport" content="width=device-width,initial-scale=1">
    """+STYLE+"""</head><body>
    <header><div class="logo">GREENMOTION ADMIN</div>
    <a href="/logout">LOGOUT</a></header>
    <div class="container">
    <h1>ADMIN DASHBOARD</h1>
    <div class="box"><h2>{{total}} Cars Listed</h2>
    <a href="/">VIEW PUBLIC WEBSITE →</a></div>

    {% if request.args.get('success') %}
    <p style="color:#39ff85">Car successfully published!</p>
    {% endif %}

    <div class="box">
    <h2>UPLOAD NEW CAR</h2>
    <form method="POST" enctype="multipart/form-data">
    <label>Car Name</label><input name="name" placeholder="Mercedes-Benz GLE 350" required>
    <label>Brand</label><input name="brand" placeholder="Mercedes" required>
    <label>Manufacturing Year</label><input name="year" type="number" placeholder="2023" required>
    <label>Price</label><input name="price" placeholder="₦45,000,000" required>
    <label>Condition</label>
    <select name="condition">
    <option>Brand New</option><option>Foreign Used</option><option>Tokunbo</option><option>Nigerian Used</option>
    </select>
    <label>Transmission</label>
    <select name="transmission"><option>Automatic</option><option>Manual</option></select>
    <label>Description</label><textarea name="description" rows="4" placeholder="Describe the vehicle"></textarea>
    <label>WhatsApp Number (include country code)</label>
    <input name="whatsapp" placeholder="2348012345678" required>
    <label>Car Picture</label><input type="file" name="image" accept="image/*" required>
    <button type="submit">PUBLISH CAR NOW</button>
    </form></div>

    <h2>MANAGE CARS</h2>
    <div class="grid">
    {% for c in cars %}
    <div class="card">
    <img src="{{c.image}}">
    <div class="content">
    <h3>{{c.name}}</h3>
    <p class="small">{{c.price}}<br>WhatsApp: {{c.whatsapp}}</p>
    <form method="POST" action="/delete/{{c.id}}" onsubmit="return confirm('Delete this car?')">
    <button style="background:#ff4444;color:white">DELETE CAR</button>
    </form>
    </div></div>
    {% endfor %}
    </div></div></body></html>
    """,cars=cars,total=total,request=request)

@app.route("/delete/<int:car_id>",methods=["POST"])
def delete_car(car_id):
    if not session.get("admin"):
        return redirect("/admin")
    con = db()
    car = con.execute("SELECT image FROM cars WHERE id=?",(car_id,)).fetchone()
    if car:
        if car["image"].startswith("/static/uploads/"):
            path = os.path.join(".",car["image"].lstrip("/"))
            if os.path.isfile(path):
                os.remove(path)
        con.execute("DELETE FROM cars WHERE id=?",(car_id,))
        con.commit()
    con.close()
    return redirect("/dashboard")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/admin")

init_db()

# Add demonstration vehicles without duplicating existing listings
con = db()
extra_cars = [
("Toyota Corolla","Toyota","2022","₦22,000,000","Foreign Used","Automatic","Comfortable and economical sedan.","2348012345678","https://images.unsplash.com/photo-1623869675781-80aa31012a5a?w=900"),
("Honda Accord","Honda","2021","₦28,500,000","Foreign Used","Automatic","Elegant executive sedan.","2348012345678","https://images.unsplash.com/photo-1603386329225-868f9b1ee6c9?w=900"),
("Honda CR-V","Honda","2022","₦35,000,000","Foreign Used","Automatic","Spacious and practical family SUV.","2348012345678","https://images.unsplash.com/photo-1519641471654-76ce0107ad1b?w=900"),
("Lexus LX 570","Lexus","2021","₦95,000,000","Foreign Used","Automatic","Powerful luxury SUV.","2348012345678","https://images.unsplash.com/photo-1519641471654-76ce0107ad1b?w=900"),
("Mercedes-Benz C300","Mercedes","2021","₦38,000,000","Foreign Used","Automatic","Elegant executive luxury sedan.","2348012345678","https://images.unsplash.com/photo-1618843479313-40f8afb4b4d8?w=900"),
("BMW 5 Series","BMW","2022","₦52,000,000","Foreign Used","Automatic","Sporty executive sedan.","2348012345678","https://images.unsplash.com/photo-1555215695-3004980ad54e?w=900"),
("Range Rover Velar","Range Rover","2022","₦78,000,000","Foreign Used","Automatic","Modern luxury SUV.","2348012345678","https://images.unsplash.com/photo-1606664515524-ed2f786a0bd6?w=900"),
("Hyundai Tucson","Hyundai","2023","₦31,000,000","Foreign Used","Automatic","Modern SUV with comfortable interior.","2348012345678","https://images.unsplash.com/photo-1519641471654-76ce0107ad1b?w=900"),
("Kia Sportage","Kia","2022","₦29,500,000","Foreign Used","Automatic","Stylish and versatile crossover.","2348012345678","https://images.unsplash.com/photo-1519641471654-76ce0107ad1b?w=900")
]
for car in extra_cars:
    if not con.execute("SELECT id FROM cars WHERE name=?", (car[0],)).fetchone():
        con.execute("""INSERT INTO cars(name,brand,year,price,condition,
        transmission,description,whatsapp,image)
        VALUES(?,?,?,?,?,?,?,?,?)""", car)
con.commit()
con.close()


if __name__ == "__main__":
    app.run(host="0.0.0.0",port=5000,debug=True)
