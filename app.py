from flask import Flask, render_template,request,flash,redirect,url_for
from application.config import Config
from application.model import *
from application.database import db
from flask_migrate import Migrate
from flask_login import LoginManager

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    app.config['SECRET_KEY'] = 'supersecretkey'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:D:\Codes\MAD2Proj - Copy\influenze\instance\data.sqlite3'
    app.config['SECURITY_PASSWORD_SALT'] = 'my_salt'
    migrate = Migrate(app, db)
    

    with app.app_context():
        db.create_all()

        # Create initial roles if they do not exist
        if not Role.query.filter_by(name='Admin').first():
            user_datastore.create_role(name = 'Admin', description='Admin Role')
            db.session.commit()
            
        else:
            admin_role = Role.query.filter_by(name='Admin').first()

        if not Role.query.filter_by(name='Influencer').first():
            user_datastore.create_role(name = "Influencer",description = "Influencer")
            db.session.commit()
        else:
            influencer_role = Role.query.filter_by(name='Influencer').first()

        if not Role.query.filter_by(name='Sponsor').first():
            user_datastore.create_role(name = "Sponsor",description = "Sponsor")
            db.session.commit()
        else:
            sponsor_role = Role.query.filter_by(name='Sponsor').first()

        #Create an initial admin user if it does not exist
        if not User.query.filter_by(id=1).first():
            user = user_datastore.create_user(password='admin', 
                email='admin@gmail.com', 
                user_name='admin',
                user_role='Admin',
                active = True,
                id=1)
            admin_role = user_datastore.find_role("Admin")
            user_datastore.add_role_to_user(user, admin_role)
            db.session.commit()

        
        #Create an initial sponsor user
        if not User.query.filter_by(id=2).first():
            user = user_datastore.create_user( 
                password='sponsor', 
                email='sponsor@gmail.com', 
                user_name='sponsor',
                user_role='Sponsor',
                id=2,
                sponsor_id=1,
                active = True
            )
            sponsor_role = user_datastore.find_role("Sponsor")
            user_datastore.add_role_to_user(user, sponsor_role)

            # Commit the changes to the database
            db.session.commit()

            
        if not User.query.filter_by(id=3).first():
            user = user_datastore.create_user( 
                password='influencer', 
                email='influencer@gmail.com', 
                user_name='influencer',
                user_role='Influencer',
                id=3,
                influencer_id=1,
                active = True
            )
            influencer_role = user_datastore.find_role("Influencer")
            user_datastore.add_role_to_user(user, influencer_role)

            # Commit the changes to the database
            db.session.commit()

        # Create dummy influencer details if it doesn't exist
        if not Influencer.query.filter_by(influencer_id=1).first():
            influencer = Influencer(influencer_reach=0, influencer_rating=0)
            db.session.add(influencer)
        
        # Create dummy sponsor details if it doesn't exist
        if not Sponsor.query.filter_by(sponsor_id=1).first():
            sponsor = Sponsor(sponsor_company='None')
            db.session.add(sponsor)
        
        if not Campaign.query.filter_by(campaign_id='1').first():
            campaign = Campaign(campaign_id='1',campaign_name='Campaign',revenue_expected=0,campaign_niche="Niche",sponsor_id=1,campaign_approval="N")
            niche = Niche.query.filter_by(niche_name=campaign.campaign_niche).first()
            if not niche:
                niche = Niche(niche_name=campaign.campaign_niche, niche_population=1000)
                db.session.add(niche)
            else:
                niche=Niche.query.filter_by(niche_name=campaign.campaign_niche).first()
                niche.niche_population = niche.niche_population+1

            campaign.campaign_niches.append(niche)
            db.session.add(campaign)
            
        
        db.session.commit()


    return app

app = create_app()

from application.routes import *


if __name__ == '__main__':
    app.run(debug=True)