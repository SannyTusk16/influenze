from application.database import db
from flask_security import Security, UserMixin, RoleMixin, SQLAlchemyUserDatastore
from flask_security.models import fsqla_v3 as fsqla
import uuid

fsqla.FsModels.set_db_info(db)

roles_users = db.Table('roles_users',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id'), primary_key=True),
    extend_existing=True
)

class Advertisement(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    niche_id = db.Column(db.Integer, db.ForeignKey('niche.niche_id'))
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.campaign_id'))
    influencer_id = db.Column(db.Integer, db.ForeignKey('influencer.influencer_id'))
    status = db.Column(db.String(20))
    advertisement_name=db.Column(db.String(30))
    budget=db.Column(db.Integer)
    


    def __repr__(self):
        return f'<Advertisements {self.id}>'





class Campaign(db.Model):
    campaign_id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    sponsor_id = db.Column(db.Integer, db.ForeignKey('sponsor.sponsor_id'),nullable=False)
    campaign_name = db.Column(db.String(80))
    revenue_expected = db.Column(db.Integer)
    revenue_received = db.Column(db.Integer, nullable=True)
    success_rate = db.Column(db.Integer, nullable=True)
    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)
    campaign_niche = db.Column(db.String(80), db.ForeignKey('niche.niche_name'))
    advertisement_id=db.Column(db.Integer,db.ForeignKey('advertisement.id'))
    campaign_approval = db.Column(db.String(1))
    visibility=db.Column(db.String(1),nullable=True)
    
    
    campaign_niches = db.relationship('Niche', secondary='campaign_niche_association', back_populates='niche_campaigns')
    def __repr__(self):
        return f'<Campaign {self.campaign_name}>'






class Fund(db.Model):
    fund_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    influencer_id = db.Column(db.Integer, db.ForeignKey('influencer.influencer_id'))
    sponsor_id=db.Column(db.Integer,db.ForeignKey('sponsor.sponsor_id'))
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.campaign_id'))
    amount = db.Column(db.Integer)

    def __repr__(self):
        return f'<fund {self.campaign_id}>'
    







class Influencer(db.Model):
    influencer_id= db.Column(db.Integer,primary_key=True,autoincrement=True)
    influencer_advertisement=db.Column(db.Integer,db.ForeignKey('advertisement.id'))
    influencer_fund=db.Column(db.Integer,db.ForeignKey('fund.fund_id'))
    influencer_user = db.Column(db.Integer,db.ForeignKey('user.id'))
    influencer_reach = db.Column(db.Integer)
    influencer_rating = db.Column(db.Float)
    

    def __repr__(self):
        return f'<Influencer {self.influencer_id}>'





class Niche(db.Model):
    niche_id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    parent_niche = db.Column(db.String(80),nullable=True)
    niche_name = db.Column(db.String(80))
    niche_population = db.Column(db.Integer)
    niche_campaigns = db.relationship('Campaign', secondary='campaign_niche_association', back_populates='campaign_niches')

    def __repr__(self):
        return f'<Niche {self.niche_name}>'





class Role(db.Model,RoleMixin):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f'<Role {self.id}>'






class Sponsor(db.Model):
    sponsor_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    sponsor_fund=db.Column(db.Integer,db.ForeignKey('fund.fund_id'))
    sponsor_company=db.Column(db.String(80),nullable=False)
    sponsor_campaign=db.Column(db.Integer,db.ForeignKey('campaign.campaign_id'))
    
    
    
    def __repr__(self):
        return f'<Sponsor {self.sponsor_company}>'





    
class User(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    password = db.Column(db.String(80), nullable=True)
    user_role = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    user_name = db.Column(db.String(80), nullable=False)
    influencer_id=db.Column(db.Integer,db.ForeignKey('influencer.influencer_id'),nullable=True)
    sponsor_id=db.Column(db.Integer,db.ForeignKey('sponsor.sponsor_id'),nullable=True)
    active = db.Column(db.Boolean,nullable = False)
    fs_uniquifier = db.Column(db.String(64),unique = True,nullable = False,default=str(uuid.uuid4()))
    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))
    

    
    def if_sponsor(self,company):
        if(self.user_role=='Sponsor'):
            sponsor_entry = Sponsor(
                sponsor_company=company
            )
            db.session.add(sponsor_entry)
            self.sponsor_id=sponsor_entry.sponsor_id
    
                
    def if_influencer(self,reach):  
        if(self.user_role=='Influencer'):
            influencer_entry = Influencer(
                id=self.id,
                password=self.password,
                user_role=self.user_role,
                email=self.email,
                user_name=self.user_name,
                influencer_reach=reach
            )
            db.session.add(influencer_entry)

    def __repr__(self):
        return f'<User {self.id}>'



#----------------------------------------------RELATION TABLES----------------------------------------------
#----------------------------------------------RELATION TABLES----------------------------------------------
#----------------------------------------------RELATION TABLES----------------------------------------------
#----------------------------------------------RELATION TABLES----------------------------------------------
#----------------------------------------------RELATION TABLES----------------------------------------------
#----------------------------------------------RELATION TABLES----------------------------------------------
#----------------------------------------------RELATION TABLES----------------------------------------------
#----------------------------------------------RELATION TABLES----------------------------------------------
#----------------------------------------------RELATION TABLES----------------------------------------------
#----------------------------------------------RELATION TABLES----------------------------------------------
#----------------------------------------------RELATION TABLES----------------------------------------------
#----------------------------------------------RELATION TABLES----------------------------------------------
#----------------------------------------------RELATION TABLES----------------------------------------------
#----------------------------------------------RELATION TABLES----------------------------------------------
#----------------------------------------------RELATION TABLES----------------------------------------------

class CampaignNiche(db.Model):
    __tablename__='campaign_niche_association'
    campaign_niche_id = db.Column(db.Integer, primary_key=True)
    niche_id = db.Column(db.Integer, db.ForeignKey('niche.niche_id'))
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.campaign_id'))
    
    def __repr__(self):
        return f'<CampaignNiche {self.campaign_niche_id}>'
    



    

user_datastore = SQLAlchemyUserDatastore(db, User, Role)