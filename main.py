from flask import Flask, render_template,request,flash,redirect,url_for
from application.config import Config
from application.database import db
from application.model import *
from application.routes import *

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    with app.app_context():
        db.create_all()

        # Create initial roles if they do not exist
        if not Role.query.filter_by(name='Admin').first():
            admin_role = Role(name='Admin', description='Admin Role')
            db.session.add(admin_role)
        else:
            admin_role = Role.query.filter_by(name='Admin').first()

        if not Role.query.filter_by(name='Influencer').first():
            influencer_role = Role(name='Influencer', description='Influencer/Advertiser')
            db.session.add(influencer_role)
        else:
            influencer_role = Role.query.filter_by(name='Influencer').first()

        if not Role.query.filter_by(name='Sponsor').first():
            sponsor_role = Role(name='Sponsor', description='Funds the campaigns/ads')
            db.session.add(sponsor_role)
        else:
            sponsor_role = Role.query.filter_by(name='Sponsor').first()

        #Create an initial admin user if it does not exist
        if not User.query.filter_by(user_id=1).first():
            admin_user = User( 
                user_password='admin', 
                user_mail='admin@gmail.com', 
                user_name='admin',
                user_role='Admin',
                user_id=1
            )
            admin_user.user_roles.append(admin_role)
            db.session.add(admin_user)
        
        if not User.query.filter_by(user_id=2).first():
            sponsor_user = User( 
                user_password='sponsor', 
                user_mail='sponsor@gmail.com', 
                user_name='sponsor',
                user_role='Sponsor',
                user_id=2,
                sponsor_id=1,
            )
            sponsor_user.user_roles.append(sponsor_role)
            db.session.add(sponsor_user)
            
        if not User.query.filter_by(user_id=3).first():
            influencer_user = User( 
                user_password='influencer', 
                user_mail='influencer@gmail.com', 
                user_name='influencer',
                user_role='Influencer',
                user_id=3,
                influencer_id=1,
            )
            influencer_user.user_roles.append(influencer_role)
            db.session.add(influencer_user)
        
        # Create dummy influencer details if it doesn't exist
        if not Influencer.query.filter_by(influencer_id=1).first():
            admin_role = Influencer(influencer_reach=0, influencer_rating=0)
            db.session.add(admin_role)
        
        # Create dummy sponsor details if it doesn't exist
        if not Sponsor.query.filter_by(sponsor_id=1).first():
            admin_role = Sponsor(sponsor_company='None')
            db.session.add(admin_role)
        
        #Dummy Campaign  
        if not Campaign.query.filter_by(campaign_id='1').first():
            admin_role = Campaign(campaign_id='1',campaign_name='Campaign',revenue_expected=0,campaign_niche="Niche",sponsor_id=1)
            db.session.add(admin_role)
        
        #DUmmy Niche    
        if not Niche.query.filter_by(niche_id='1').first():
            admin_role = Niche(niche_id='1',niche_name='Niche',niche_population=1000)
            db.session.add(admin_role)
        
        db.session.commit()
    
    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)