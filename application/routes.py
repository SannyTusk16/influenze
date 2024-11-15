from flask import render_template, request, redirect, url_for, flash, session,make_response
from app import app, db
from datetime import datetime
from application.database import db
import application.tasks 
from application.model import *
from flask_security import LoginForm,logout_user,Security,current_user 
from flask_login import login_user # Import login_user from flask_login
from werkzeug.security import check_password_hash
from flask_security.utils import verify_password
from flask_login import LoginManager

login_manager = LoginManager()
login_manager.init_app(app)
security = Security(app, user_datastore)

@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(id=user_id)

def render_with_no_cache(template_name, **context):
    """Helper function to render a template with cache disabled."""
    response = make_response(render_template(template_name, **context))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    return response



@app.route("/")
def index():
    return render_template('base.html')

@app.route("/sponsorlogin", methods=['GET', 'POST'])
def sponsor_login():
    form = LoginForm()
    if request.method == 'POST' and form.validate_on_submit():
        
        user = User.query.filter_by(email=form.email.data).first()
        
        if user and verify_password(form.password.data, user.password):
            # Log the user in to set up session and make current_user available
            login_user(user)
            session['id'] = user.id
            session['sponsor_id'] = user.sponsor_id
            session['influencer_id'] = user.influencer_id
            session['user_name']  = user.user_name
            sponsor = Sponsor.query.filter_by(sponsor_id=user.sponsor_id).first()
            campaign = Campaign.query.filter_by(sponsor_id=user.sponsor_id).all()

            # Check if user is authenticated and print session data
            if current_user.is_authenticated:
                print(f"Session data: {session}")
                print(f"User ID is: {current_user.id}")
                print(f"Influencer ID is {user.influencer_id}")
            else:
                print("No user is logged in.")

            # Redirect to the sponsor dashboard
            application.tasks.func.delay()
            return render_with_no_cache('sponsor_dashboard.html', campaign=campaign, user=user, sponsor=sponsor)
        else:
            # If authentication fails
            flash('Incorrect credentials')
            print("Wrong Credentials")
    
    # Render the login page for GET requests
    return render_template('login_sponsor.html',form = form)
        
@app.route("/sponsor_register", methods=['GET', 'POST'])
def sponsor_register():
    if request.method == 'GET':
        return render_template('sponsor_register.html')
    if request.method == 'POST':
        if request.form.get('user_password') != request.form.get('user_confirm_password'):
            flash('Passwords do not match')
            return render_template('sponsor_register.html')
        
        user_name = request.form.get('user_name')
        email = request.form.get('user_email')
        password = request.form.get('user_password')
        user_role = "Sponsor"
        sponsor_company=request.form.get('company')
        
        print(sponsor_company)
        my_sponsor = User(
            user_role=user_role,
            user_name=user_name,
            email=email,
            password=password,
            active = True,
        )   
        
        sponsor_entry = Sponsor(sponsor_company=sponsor_company)
        
        db.session.add(sponsor_entry)
        db.session.commit()
        my_sponsor.sponsor_id=sponsor_entry.sponsor_id

        db.session.add(my_sponsor)
        db.session.commit()
        return redirect(url_for('sponsor_login'))

@app.route("/sponsor/dashboard", methods=['GET','POST'])
def sponsor_dashboard():
    if request.method == 'GET':
        campaign = Campaign.query.filter_by(sponsor_id=session['sponsor_id']).all()
        user = User.query.filter_by(user_name=session['user_name']).first()
        sponsor = Sponsor.query.filter_by(sponsor_id=user.sponsor_id).first()
        return render_with_no_cache('sponsor_dashboard.html', campaign=campaign, user=user, sponsor=sponsor)
    if request.method =='POST':
        sponsor = Sponsor.query.filter_by(sponsor_id=session['sponsor_id']).first()
        campaign = Campaign.query.filter_by(sponsor_id=session['sponsor_id']).all()
        
        campaign_id=request.form.get('campaign_id')
        campaign_advertisement=Advertisement.query.filter_by(campaign_id=campaign_id)
        return render_template('campaign_advertisement.html',campaign_advertisement=campaign_advertisement,campaign=campaign)

@app.route("/sponsor/new_campaign", methods=['GET', 'POST'])
def new_campaign():
    if request.method == 'GET':
        return render_template('new_campaign.html')
    if request.method == 'POST':
        print(f"Current Sponsor ID {current_user.sponsor_id}")
        sponsor_id=current_user.sponsor_id
        sponsor=Sponsor.query.filter_by(sponsor_id=sponsor_id)
        id=session.get('id')
        user=User.query.filter_by(id=id)
        new_campaign_name = request.form.get('campaign_name')
        new_campaign_revenue_expected = request.form.get('revenue_expected')
        new_campaign_start_date0 = request.form.get('start_date')
        new_campaign_end_date0 = request.form.get('end_date')
        new_campaign_niche = request.form.get('niche_name')
        new_campaign_sponsor =  session.get('sponsor_id')
        
        if request.form.get('visibility') != 'No':
            new_campaign_visibility='Y'
        else:
            new_campaign_visibility='N'
            
    
        new_campaign_end_date = datetime.strptime(new_campaign_end_date0, '%Y-%m-%d')
        new_campaign_start_date = datetime.strptime(new_campaign_start_date0, '%Y-%m-%d')

        new_campaigns = Campaign(
            campaign_name=new_campaign_name,
            revenue_expected=new_campaign_revenue_expected,
            start_date=new_campaign_start_date,
            end_date=new_campaign_end_date,
            campaign_niche=new_campaign_niche,
            sponsor_id = new_campaign_sponsor,
            visibility=new_campaign_visibility
        )

        niche = Niche.query.filter_by(niche_name=new_campaign_niche).first()
        if not niche:
            niche = Niche(niche_name=new_campaign_niche, niche_population=1000)
            db.session.add(niche)
        else:
            niche=Niche.query.filter_by(niche_name=new_campaign_niche).first()
            niche.niche_population = niche.niche_population+1

        new_campaigns.campaign_niches.append(niche)
        db.session.add(new_campaigns)
        db.session.commit()

        return redirect(url_for('sponsor_dashboard',sponsor=sponsor,user=user))




@app.route('/campaign',methods=['GET','POST'])  
def campaign_advertisement():
    if request.method == 'POST':
        influencer_id=request.form.get('influencer_id')
        advertisement_name=request.form.get('advertisement_name')   
        budget = request.form.get('budget')
        campaign_id=request.form.get('campaign_id')
        campaign_niche= CampaignNiche.query.filter_by(campaign_id=campaign_id).first()
        niche_id = campaign_niche.niche_id
        print("NicheID/campaign ")
        print(niche_id)
        
        if request.form.get('response') :
            new_advertisement = Advertisement(influencer_id=influencer_id,advertisement_name=advertisement_name,budget=budget,status='Requested',campaign_id=campaign_id,niche_id=niche_id)
            db.session.add(new_advertisement)
            db.session.commit() 
        print("campaignID/campaign")
        print(campaign_id)
        campaign = Campaign.query.filter_by(campaign_id=campaign_id).first()
        campaign_advertisement=Advertisement.query.filter_by(campaign_id=campaign_id).all()
        return render_template('campaign_advertisement.html',campaign_advertisement=campaign_advertisement,campaign=campaign)

            
@app.route('/sponsor/campaign/delete_campaign', methods=['POST'])
def delete_campaign():
    campaign_id = request.form.get('campaign_id')
    campaign = Campaign.query.filter_by(campaign_id=campaign_id).first()
    campaign_niche=CampaignNiche.query.filter_by(campaign_id=campaign_id).first()
    niche=Niche.query.filter_by(niche_id=campaign_niche.niche_id).first()
    db.session.delete(campaign_niche)
    db.session.delete(campaign)
    if(niche.niche_population>1000):
        niche.niche_population-=1
    else:
        db.session.delete(niche)
    db.session.commit()
    flash('Campaign deleted successfully.')
    return redirect(url_for('sponsor_dashboard'))

@app.route('/campaign/new_advertisement',methods=['POST'])
def add_advertisement():
    if request.method=='POST':
        campaign_id=request.form.get('campaign_id')
        campaign_niche=request.form.get('campaign_niche')
        campaign_influencer=request.form.get('influencer_id')
        print("Campaign##ID")
        print(campaign_id)
        print(campaign_niche)
        
        niche=CampaignNiche.query.filter_by(campaign_id=campaign_id).first()
        
        return render_template('new_advertisement.html',campaign_id=campaign_id,niche_id=niche.niche_id,influencer_id=campaign_influencer)

@app.route('/sponsor/campaign/delete_advertisement', methods=['POST'])
def delete_advertisement():
    id = request.form.get('id')
    print('id')
    print(id)
    advertisement = Advertisement.query.filter_by(id=id).first()
    db.session.delete(advertisement)
    db.session.commit()
    flash('Campaign deleted successfully.')
    campaign_id = request.form.get('campaign_id')
    campaign = Campaign.query.filter_by(campaign_id=campaign_id).first()
    campaign_advertisement=Advertisement.query.filter_by(campaign_id=campaign_id).all()
    return render_template('campaign_advertisement.html',campaign_advertisement=campaign_advertisement,campaign=campaign)

@app.route('/sponsor/campaign/edit_advertisement', methods=['POST'])
def edit_advertisement():
    if request.method=='POST':
        id = request.form.get('id')
        print('advertisement   2')
        print(id)
        advertisement = Advertisement.query.filter_by(id=id).first()
        return render_template("edit_advertisement.html",advertisement = advertisement)
    

@app.route('/sponsor/edit_advertisement/confirm',methods=['GET','POST'])
def confirm_update_advertisement():
    if request.method=='POST':
        print('advertisement   12')
        print(request.form.get('id'))          
        edit_advertisement=Advertisement.query.filter_by(id=int(request.form.get('id'))).first()
        
        print("Edited Advertisement")
        print(edit_advertisement.id)    
        print("uau2")
        
        edit_advertisement.advertisement_name=request.form.get('advertisement_name')
        edit_advertisement.influencer_id=int(request.form.get('influencer_id'))
        edit_advertisement.budget=request.form.get('budget')
        
        db.session.commit()
        
        print(session['id'])
        return redirect(url_for('sponsor_dashboard'))

@app.route("/sponsor/campaign_update" ,methods=['GET','POST'])
def update_campaign():
    if request.method=='POST':
        campaign_id = request.form.get('campaign_id')
        print('campaign   2')
        print(campaign_id)
        campaign = Campaign.query.filter_by(campaign_id=campaign_id).first()
        return render_template("update_campaign.html",campaign = campaign)

@app.route('/sponsor/campaign_update/confirm',methods=['GET','POST'])
def confirm_update_campaign():
    if request.method=='POST':
        print('campaign   12')
        print(request.form.get('campaign_id'))          
        edit_campaign=Campaign.query.filter_by(campaign_id=int(request.form.get('campaign_id'))).first()
        
        print("Edited Campaign")
        print(edit_campaign.campaign_id)    
        print("uau")
        
        edit_campaign.campaign_name=request.form.get('campaign_name')
        edit_campaign.revenue_expected=int(request.form.get('revenue_expected'))
        edit_campaign.start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d').date()
        edit_campaign.start_date = datetime.strptime(request.form.get('end_date'), '%Y-%m-%d').date()
        old_niche = Niche.query.filter_by(niche_name = edit_campaign.campaign_niche).first()
        old_niche.niche_population-=1
        
        if(Niche.query.filter_by(niche_name=request.form.get('campaign_niche')).first()):
            new_niche=Niche.query.filter_by(niche_name=request.form.get('campaign_niche')).first()
            new_niche.niche_population+=1
        else:
            new_niche = Niche(
                niche_name = request.form.get('campaign_niche'),
                niche_population = 1000
            )
            db.session.add(new_niche)
        
        db.session.commit()
        
        campaignNiche = CampaignNiche.query.filter_by(campaign_id=int(request.form.get('campaign_id'))).first()
        
        new_niche = Niche.query.filter_by(niche_name=request.form.get('campaign_niche')).first()
        
        campaignNiche.niche_id = new_niche.niche_id 
        
        edit_campaign.campaign_niche=request.form.get('campaign_niche')
        
        db.session.commit()
        
        print(session['id'])
        return redirect(url_for('sponsor_dashboard'))
    
@app.route('/sponsor/update', methods=['GET','POST'])
def sponsor_update():
    if(request.method=='GET'):
        return render_template('update_sponsor.html')
    if(request.method=='POST'):
        
        new_user=User.query.filter_by(id=session['id']).first()
        
        new_user.user_name = request.form.get('user_name')
        new_user.password = request.form.get('user_password')
        
        if(session['user_role']=='Sponsor'):
            sponsor_id=new_user.sponsor_id 
            new_sponsor=Sponsor.query.filter_by(sponsor_id=sponsor_id)
            new_sponsor.sponsor_company=request.form.get('company')
        db.session.commit()
        session.pop('user', None)
        return redirect(url_for("index"))
        
@app.route('/sponsor/negotiation')
def negotiation_requests():
    if request.method=='GET':
        sponsor_id=session.get('id')
        sponsor_id=User.query.filter_by(id=sponsor_id).first()
        sponsor_id=sponsor_id.sponsor_id
        print("Sponosr ID")
        print(sponsor_id)
        a=[]
        campaign = Campaign.query.filter_by(sponsor_id=sponsor_id).all()
        for i in campaign:
            advertisements = Advertisement.query.filter_by(campaign_id=i.campaign_id).filter(Advertisement.status.notin_(['Requested', 'Accepted', 'Rejected'])).all()
            a.append(advertisements)
        return render_template('negotiation_requests.html',a=a)

@app.route("/influencerlogin", methods=['GET', 'POST'])
def influencer_login():
    form = LoginForm()
    if request.method == 'POST' and form.validate_on_submit():
        
        user = User.query.filter_by(email=form.email.data).first()
        
        if user and verify_password(form.password.data, user.password):
            # Log the user in to set up session and make current_user available
            login_user(user)
            session['id'] = user.id
            session['sponsor_id'] = user.sponsor_id
            session['influencer_id'] = user.influencer_id
            session['user_name']  = user.user_name

            # Check if the user is authenticated
            if current_user.is_authenticated:
                # Debugging session and user data
                print(f"Session data: {session}")
                print(f"User ID is: {current_user.id}")
                print(f"Influencer ID is: {user.influencer_id}")
            else:
                print("No user is logged in.")

            # Fetch influencer-specific data
            influencer = Influencer.query.filter_by(influencer_id=user.influencer_id).first()
            advertisements = Advertisement.query.filter_by(influencer_id=influencer.influencer_id).all()
            advertisement_request = [ad for ad in advertisements if ad.status == 'Requested']

            # Render the influencer dashboard with the relevant data
            return render_with_no_cache('influencer_dashboard.html', user=user, influencer=influencer,
                                        advertisements=advertisements, advertisement_request=advertisement_request)
        else:
            # Handle incorrect credentials
            flash("Incorrect email or password. Please try again.", "danger")
            print("Wrong credentials")

    # Render the login page for GET requests or failed login attempts
    return render_template('login_influencer.html',form = form)
@app.route("/influencer_register", methods=['GET', 'POST'])
def influencer_register():
    if request.method == 'GET':
        return render_template('influencer_register.html')
    if request.method == 'POST':
        if request.form.get('user_password') != request.form.get('user_confirm_password'):
            flash('Passwords do not match')
            return render_template('influencer_register.html')

        user_name = request.form.get('user_name')
        user_email = request.form.get('user_email')
        password = request.form.get('user_password')
        user_role = "Influencer"
        influencer_reach=request.form.get('reach')
        
        influencer_entry=Influencer(influencer_reach=influencer_reach)
        db.session.add(influencer_entry)
        db.session.commit()

        my_influencer = User(
            user_role=user_role,
            user_name=user_name,
            email=user_email,
            password=password,
            active = True
        )
        
        my_influencer.influencer_id=influencer_entry.influencer_id
        
        db.session.add(my_influencer)
        db.session.commit()
        return redirect(url_for('influencer_login'))
    
@app.route('/influencer',methods=['GET','POST'])
def influencer_dashboard():
    if(request.method=='POST'):
        if(request.form.get('accept')):
            advertisement_id=request.form.get('accept')
            advertisement_update=Advertisement.query.filter_by(id=advertisement_id).first()
            
            advertisement_update.status='Accepted'
            
            db.session.commit()
        
        if(request.form.get('reject')):
            advertisement_id=request.form.get('reject')
            advertisement_update=Advertisement.query.filter_by(id=advertisement_id).first()
            
            advertisement_update.status='Rejected'
            
            db.session.commit()
            
        if(request.form.get('negotiate')):
            advertisement_id=request.form.get('negotiate')
            advertisement_update=Advertisement.query.filter_by(id=advertisement_id).first()
            
            advertisement_update.budget+=int(request.form.get('value'))
            advertisement_update.status = 'Negotiated'
            
            db.session.commit()
            
        influencer=Influencer.query.filter_by(influencer_id=advertisement_update.influencer_id).first()
        
        user = User.query.filter_by(influencer_id=influencer.influencer_id)
            
        advertisements=Advertisement.query.filter_by(influencer_id=influencer.influencer_id)
        
        advertisement_request=advertisements.filter_by(status='Requested')

        return render_template('influencer_dashboard.html',user=user,influencer=influencer,advertisements=advertisements,advertisement_request=advertisement_request)
        
@app.route("/adminlogin", methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('user_name')
        password = request.form.get('user_password')
        mail = request.form.get('user_email')
        
        advertisements = Advertisement.query.all()
        users = User.query.all()
        campaigns = Campaign.query.all()
        
        admin = User.query.filter_by(email = mail).first()
        
        session['id'] = admin.id
        session['sponsor_id'] = admin.sponsor_id
        session['influencer_id'] = admin.influencer_id
        session['user_name']  = admin.user_name
        
        if admin.user_role != 'Admin':
            flash('Not an Admin')
            return redirect(url_for('admin_login'))

        user = User.query.filter_by(user_name=username).first()
        if not user:
            flash('User Not Found')
            return redirect(url_for('admin_login'))

        if user.password == password:
            return render_with_no_cache('admin_dashboard.html', users=users, advertisements=advertisements, campaigns=campaigns)
        else:
            flash('Incorrect Password Entered')
    return render_template('login_admin.html')


@app.route("/logout")
def logout():
    # Log the user out with Flask-Security's logout function
    logout_user()

    # Clear the session to remove any additional data
    session.clear()

    # Redirect to the index or login page
    return redirect(url_for('index'))
    


@app.route('/search',methods=['GET','POST'])
def search():
    if request.method =='GET':
        isInfluencer = True
        if session['user_role'] == 'Sponsor':
            isInfluencer = False
        campaigns = Campaign.query.filter_by(visibility='Y').all()
        users = User.query.filter_by(user_role='Influencer').filter(User.active != True).all()
        return render_template('search.html',users=users,campaigns=campaigns,isInfluencer = isInfluencer)
    if request.method == 'POST':
        search = request.form.get('search')
        if not search:
            flash('Please enter search keyword')
            return redirect(url_for('index'))
        
        isInfluencer = True
        if session['user_role'] == 'Sponsor':
            isInfluencer = False
        
        campaigns = Campaign.query.filter_by(campaign_name = search).all()
        user = User.query.filter_by(user_name = search).all()        
        print(session['user_name'])
        
        print("Campaigns")
        for i in campaigns:
            print(i)

        print("User")
        for i in user:
            print(i)
        return render_template('search.html',users=user,campaigns=campaigns,isInfluencer = isInfluencer)
    
    
@app.route('/search/influencer/advertisements',methods=['GET','POST'])
def influencer_advertisements():
    if request.method=='POST':
        influencer_id = request.form.get('influencer_id')
        
        user = User.query.filter_by(influencer_id = influencer_id).first()
        
        
        influencer_advertisements = Advertisement.query.filter_by(influencer_id = influencer_id).all()
        
        for i in influencer_advertisements:
            print(i.id)
    
        influencer = Influencer.query.filter_by(influencer_id = influencer_id).first()
        
        return render_template('search_influencer_advertisement.html',user= user,influencer_advertisements=influencer_advertisements,influencer = influencer)
        
        
@app.route('/search/campaign/advertisement',methods=['GET','POST'])
def search_campaign_advertisement():    
    if request.method=='POST':
        print("oompa")
        campaign_id = request.form.get('campaign_id')
        print(session['influencer_id'])
        
        print(request.form.get('campaign_id'))
        
        campaign_advertisement = Advertisement.query.filter_by(campaign_id = campaign_id).all()
    
        
        return render_template('search_campaign_advertisement.html',campaign_advertisement = campaign_advertisement,campaign = Campaign.query.filter_by(campaign_id=campaign_id).first(),influencer_id=session['influencer_id'])


@app.route('/admin_flag',methods=['POST'])
def admin_flag():
    id = request.form.get('id')
    user = User.query.filter_by(id=id).first()
    user.active = True if user.active is None else ('No' if user.active == True else False)
    db.session.commit()

    users = User.query.all()
    campaigns = Campaign.query.all()
    advertisements = Advertisement.query.all()
    return render_with_no_cache('admin_dashboard.html', users=users, campaigns=campaigns, advertisements=advertisements)
    
@app.route('/admin_approval',methods=['GET','POST'])
def admin_approval():
    if request.method=="POST":
        campaign_id=request.form.get('campaign_id')
        
        print(campaign_id)
        
        campaign=Campaign.query.filter_by(campaign_id=campaign_id).first()
        
        if(campaign.campaign_approval=="Y"):
            campaign.campaign_approval="N"
        if(campaign.campaign_approval=="N"):
            campaign.campaign_approval="Y"
        
        db.session.commit()
        
        users=User.query.all()
        
        campaigns = Campaign.query.all()
        
        advertisements = Advertisement.query.all()
        
        return render_template('admin_dashboard.html',users=users,campaigns=campaigns,advertisements=advertisements)